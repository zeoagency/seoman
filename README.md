# Seoman - A Command Line Interface that is designed for technical SEOs

## Requirements

* Python 3.6+


## Installation


```python
pip install seoman
```

## Features

<h2 align="center">Authentication</h2>

with `seoman auth` authentication is as easy as using Google's Search Console, you 'll we redirected to the web browser. Once you have done, we will save your credentials for re-use. So you will never need to re-auth again till your credentials gets expired.

<h2 align="center">Exporting</h2> 

With seoman you can export your data in 5 different formats. 

* **JSON**
* **CSV**
* **XLSX**
* **TSV**
* **Table(For exploring in Command Line)**

So you can get your data with seoman and analyze in anything from Python to Excel, R etc.

<h2 align="center">Easy to Use</h2> 

Seoman is designed to be a CLI that can every person use it easily. With seoman's query logic you can create your queries interactively with`seoman query add` it will save them, and you can re-run them again and again with `seoman query run`, You can see the details of your query with `seoman query show` and you can delete it with `seoman query delete`.

```bash
Commands:
  add     Build a query interactively.
  delete  Delete a query.
  run     Select a query then run it.
  show    Show details from selected query.
```


<h2 align="center">Unlimited Data</h2>

Seoman has a own logic for big accounts, with Google Search Console you can not fetch more than 5000 results per day. But with seoman it is up to you. 

So imagine you want to get your data between 20 August to 27 August. 

Seoman asks you to set a frequency 

```
[?] How frequently you would like to get your data between 11 Oct 2020 and 31 Oct 2020: daily
 > daily
   twodaily
   threedaily
   fourdaily
   fivedaily
   sixdaily
   weekly
   ...
```

So when you specify your start and end date you will have a fully control to your data. Also there is more! If there is more rows than 25000 seoman asks you for to iterate more. So you can get well-rounded datas without any effort!

------------

And many more features... 

This package is built on top of [Google's own API client for Python](https://github.com/googleapis/google-api-python-client)




## Quickstart
- Create a new project in the Google Developers Console, enable the Google Search Console API under "APIs & Services". Next, create credentials for an OAuth client ID, choosing the Other Application type. Download a JSON copy of your client secrets. If you already have a project just Download a copy of your client secrets.
- Install seoman
- That's it! You can start using your app with your `client_secrets.json`
