About
-------

CKAN extension sending notification to the remote endpoints about resources when resource was uupdated.

Installation
-------

Activate ckan virtualenv: 
```bash
. /usr/lib/ckan/default/bin/activate
```

Start the installation from the extension directory:
```bash
cd ckanext-notification_api
python setup.py develop
```

Add extension to ckan config, typically ```/etc/ckan/default/production.ini```:

```ApacheConf
[app:main]
ckan.plugins = ... notification_api
```

Usage
-------

This extension provides two actions:
- notification_subscribe
- notification_unsubscribe

They can be called via API like /api/3/action/notification_subscribe and /api/3/action/notification_subscribe .
As an input is considered JSON with values entity_id and url .

The normal usecase would be:

Subscribe notification of given resource id and receiving notifications of given url.
For this purpose you need to send POST request to endpoint /api/3/action/notification_subscribe with user's API key in request header and request body as following:
```json
{"entity_id" : "<resource_id>",
 "url" : "<url>"}
```

If the response looks like the JSON below, the subscription was successful.
```json
{ ...
 "success" : true,
  ... }
```

Unsubscribe notification of given resource id and url.
For this purpose you need to send POST request to endpoint /api/3/action/notification_unsubscribe with user's API key (same API key that was used for subscribe call) in request header and request body as following:
```json
{"entity_id" : "<resource_id>",
 "url" : "<url>"}
```

If the response looks like the JSON below, the subscription was successful.
```json
{ ...
 "success" : true,
  ... }
```

When the change occures, the notification will be sent to the registred url.
Notification is a POST request in the following form:

```bash
POST / HTTP/1.1
Host: <url>
Content-Type: application/json
Accept-Encoding: gzip, deflate, compress

{"status": "updated", "entity": "resource", "entity_id": "<entity_id>", "address": "<url>", "user_ref": "<user_id>", "ckan": "<ckan site url>"}
```

When the resource is deleted, notification will be in the following form:

```bash
POST / HTTP/1.1
Host: <url>
Content-Type: application/json
Accept-Encoding: gzip, deflate, compress

{"status": "deleted", "entity": "resource", "entity_id": "<entity_id>", "address": "<url>", "user_ref": "<user_id>", "ckan": "<ckan site url>"}
```


License
-------

Licensed under [GNU Affero General Public License, Version 3.0](http://www.gnu.org/licenses/agpl-3.0.html). See [LICENSE](LICENSE).
