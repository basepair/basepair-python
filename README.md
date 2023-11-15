Python client for Basepair
======================

Python bindings for Basepair's API and command line interface (CLI).

## Using MFA
**Note: It is advisable to use MFA for increased security and best practices**

After you have been added to the list of collaborators, you can verify if MFA has been activated for you by visiting [collaboration page](https://pypi.org/manage/project/basepair/collaboration/)
### How to build and push to pypi:

```BASH
python setup.py sdist bdist_wheel # This will create two files in a newly created dist directory, a source archive and a wheel:
twine upload dist/* # To upload it to Pypi
Uploading distributions to https://upload.pypi.org/legacy/
Enter your username:
Enter your password:
```

Note: `username` must be `__token__` (not your pypi username)
`password` is the token. You may generate the token -> [token creation page](https://pypi.org/manage/account/token/).

That is it!

Below is a successful execution sample:
```
Uploading distributions to https://upload.pypi.org/legacy/
Enter your username: __token__
Enter your password:
Uploading basepair-2.0.7-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 51.0/51.0 kB • 00:00 • 36.3 MB/s
Uploading basepair-2.0.7.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 37.4/37.4 kB • 00:00 • 47.2 MB/s

View at:
https://pypi.org/project/basepair/2.0.7/
```
