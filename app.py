from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from SearchFunctionality import perform_search, compile_results
from SubdomainEnum import enumerate_subdomains
from exportResults import export_to_excel
from waitress import serve
import os
import traceback
import sys
from urllib.parse import urlparse, unquote
import io
import threading
import time
from functools import wraps
import subprocess

app = Flask(__name__, static_folder='static')

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100000 per day", "10000 per hour"],
    storage_uri="memory://"
)

# Global variable to store enumeration results and progress
enumeration_cache = {}

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

def rate_limited(max_per_second):
    min_interval = 1.0 / float(max_per_second)
    def decorator(func):
        last_time_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_time_called[0] = time.time()
            return ret
        return wrapper
    return decorator

def update_progress(domain, scan_type, progress):
    if domain in enumeration_cache:
        enumeration_cache[domain]['progress'][scan_type] = progress

@rate_limited(1)
def background_enumerate(domain, scan_types):
    try:
        enumeration_cache[domain] = {
            'status': 'processing',
            'progress': {scan_type: 0 for scan_type in scan_types},
            'results': {},
            'scan_types': scan_types  # Store scan_types in the cache
        }
        
        def progress_callback(scan_type, progress):
            update_progress(domain, scan_type, progress)
        
        all_subdomains, results = enumerate_subdomains(domain, scan_types, progress_callback)
        
        enumeration_cache[domain] = {
            'status': 'complete',
            'results': results,
            'scan_types': scan_types  # Include scan_types in the final result
        }
    except Exception as e:
        app.logger.error(f"An error occurred during background enumeration: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        enumeration_cache[domain] = {
            'status': 'error',
            'error': str(e),
            'scan_types': scan_types  # Include scan_types even in case of error
        }

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
@limiter.limit("100 per minute")
def search_results():
    try:
        data = request.json
        query = data['query']
        num_results = int(data['num_results'])
        
        if num_results > 50 or num_results < 1:
            return jsonify({"error": "Number of results must be between 1 and 50."}), 400
        
        engines = ['Google', 'Bing', 'DuckDuckGo', 'Baidu']
        all_results = {}
        
        for engine in engines:
            engine_results = perform_search(engine, query, num_results)
            if isinstance(engine_results, list):
                all_results[engine] = engine_results
        
        compiled_results = compile_results(all_results)
        return jsonify(compiled_results)
    except Exception as e:
        app.logger.error(f"An error occurred during search: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

@app.route('/enumerate')
@limiter.limit("100 per minute")
def enumerate():
    domain = request.args.get('domain')
    scan_types = request.args.getlist('scan_types')
    if not domain:
        return redirect(url_for('index'))
    
    domain = normalize_url(domain)
    
    if not is_valid_url(domain):
        return jsonify({"error": "Invalid URL format. Please enter a valid domain (e.g., example.com)"}), 400
    
    if not scan_types:
        return jsonify({"error": "No scan types selected. Please select at least one scan type."}), 400
    
    # Start the enumeration in a background thread
    thread = threading.Thread(target=background_enumerate, args=(domain, scan_types))
    thread.start()
    
    return render_template('enumerate.html', domain=domain, processing=True, scan_types=scan_types)
@app.route('/enumeration_status/<path:domain>')
@limiter.limit("1000 per hour")  # Increased rate limit
def enumeration_status(domain):
    try:
        domain = unquote(domain)
        if domain in enumeration_cache:
            result = enumeration_cache[domain]
            result['scan_types'] = result.get('scan_types', [])  # Ensure scan_types is included
            # Include harvester results if available
            if 'harvester' in result.get('results', {}):
                result['harvester'] = result['results']['harvester']
                
            return jsonify(result)
        else:
            return jsonify({"status": "processing", "progress": {}})
    except Exception as e:
        app.logger.error(f"Error in enumeration_status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/export', methods=['POST'])
@limiter.limit("100 per hour")
def export():
    try:
        data = request.json
        domain = data['domain']
        
        # Retrieve the results from the cache
        cached_data = enumeration_cache.get(domain)
        if not cached_data or cached_data['status'] != 'complete':
            return jsonify({"error": "No completed results found for the given domain"}), 404
        
        results = cached_data['results']
        
        output = io.BytesIO()
        export_to_excel(results, domain, output)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{domain}_enumeration_results.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        app.logger.error(f"An error occurred during export: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

def normalize_url(url):
    #url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000)