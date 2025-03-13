# Simple Event-Trigger categorisation using LLM and RAG demo app

This is a simple app that tries to mimic RAG in a real life application

## What is this demo is trying to solve

Suppose a business wants to better understand their customers for whatever
reason. They could do that through gauging the customers' interactions with
their services. In the case of a bank, that would be the transactions that each
and every customer makes in their daily lives.

The quickest and arguably most effective way to understand those transactions
are through the transactions content, also known as "remark", where the users
are required to describe their transactions.

## Where do LLM and RAG come in

A rule base approach arguably works. For example, if a transaction has the term
"car payment" in it, there is a high chance that that customer is buying a car.
However, the trouble comes when the remarks comes with complicated words. For
example, abbreviation, or words and phrases that carry different meanings
depending on the context.

That is where a LLM could come into handy as it can try to understand the
context.

To further help the LLM understand the context, a file which contains the
popular words and their abbreviations is provided. This tries to mimic a
database that the LLM could look into to match the abbreviation to their
meaning. The LLM could try to decide what is the meaning of each abbreviation
given the context.

## How this demo works

The abbreviation dictionary is loaded on startup. The user can upload 2 excel
files, 1 containing the events (including "Others"), the other including the
transactions.

_NOTE:_ The event file must have an entry for "Others" or
similar phrases, as the LLM will try to match the transactions to the entries in
that file, and only entries in that file. Also, the remark column must be named
"REMARK_CLEAN" (check the sample files in `/data`)

After uploading, the program will try to search for the column "REMARK_CLEAN"
and read the remarks in that column. It will try to identify abbreviations and
make sense of what they could mean. It will utilise the help of the dictionary
where possible. It will replace the abbreviations with what it thinks are the
meanings.

After that, the program will prompt the LLM into matching the remark with a
suitable category. The hopes is that the LLM will read the remark and the
categories and understand them both, thus match the transactions to the suitable
category.

It will produce a final excel file containing the transactions and their
categories which the user can download.

## About this demo

Utilise the Mistral LLM through the Ollama framework for prompts. This model
tries to imitate the use of Retrieval-Augmented Generation, but as a very simple
state. This doesn't touch the database management process. In fact, it doesn't
have any database at all, so the different indexing, embedding and chunking
algorithms and approaches are not utilised.

That being said, this still behaves like a RAG system at a high level. It still
takes in a prompt, tries to understand it, then search a private database before
giving out a response.

More faithful and constructive ideas are always welcome!

## How to get this running

- Clone this repo (obviously)
- Install what's inside `conf/requirements.txt`:
  `pip install -r conf/requirements.txt`
- Install Ollama and Mistral.
  - Click [here](https://ollama.com/download) for instructions on installing
    Ollma
    _NOTE: If you're using Linux, it's always a good idea to read what's a
    script doing before running it instead of piping it straight into `sh` like
    the instructions._
  - After installing Ollama, run `ollma run mistral` to make sure Mistral is
    installed.
- To run the app, navigate to `src/`, then run: `streamlit run app.py`.
- Bob's your uncle!
