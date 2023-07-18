from flask import Flask ,request ,jsonify
from search import search
import html
from filter import Filter
from storage import  *

app = Flask(__name__)

style = """
<style>
.site{
    font-size: .8rem;
    color:green;
}

.snippet{
    font-size : .9rem;
    color:gray;
    margin-bottom: 30px;
}

.rel-button{
    cursor: pointer;
    color:blue;
    }
    
</style>
<script>
const relevant = function(query,link){
    fetch("/relevant",{
        method='POST',
        headers :{
            'Accept':'application/json',
            'Content-Type':'application/json',
        },
        body : JSON.stringify({
            "query":query,
            "link":link
            })
    });
}
</script>
"""


search_template = style+"""
<form action="/" method ="post">
    <input type="text" name="query">
    <input type="submit" name =search>
</form>
"""

result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}","{link}");'>relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""

def show_search_form():
    return search_template

def run_search(query):
    result = search(query)
    fi = Filter(result)
    result = fi.filter()
    rendered = search_template
    result["snippet"] = result["snippet"].apply(lambda x:html.escape(x))
    for index,row in result.iterrows():
        rendered+= result_template.format(
            **row
        )

    return rendered


@app.route("/",methods=["GET","POST"])
def search_form():
    if request.method == "POST":
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()


@app.route("/relevant" , methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query,link,10)
    return jsonify(success=True)