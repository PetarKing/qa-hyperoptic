from __future__ import print_function
import os
import json

import pprint
pp = pprint.PrettyPrinter(indent=1)

from flask import Flask, request, jsonify, render_template
import requests

from database import get_q_test_coverage_per_member

# Initialize application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getCoverageBySprint', methods=['POST'])
def get_q_test_coverage_per_sprint():
    sprints = request.get_json()['sprins']
    results = get_q_test_coverage_per_member(sprints)
    return results
