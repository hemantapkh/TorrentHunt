"""Application services: glue between external interfaces and the app.

Services own their session scopes because they are called from outside
handler session boundaries (e.g. by the search provider).
"""
