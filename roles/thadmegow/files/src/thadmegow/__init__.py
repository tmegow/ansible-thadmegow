from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'
