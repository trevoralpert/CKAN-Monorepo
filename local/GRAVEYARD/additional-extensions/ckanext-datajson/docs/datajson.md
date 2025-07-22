# Data.json

The following documents tips and nice-to-know things about enabling the
`datajson` plugin.


## Configuration

You can customize the URL that generates the data.json output:

	ckanext.datajson.path = /data.json
	ckanext.datajsonld.path = /data.jsonld
	ckanext.datajsonld.id = http://www.youragency.gov/data.json

You can enable or disable the Data.json output by setting

    ckanext.datajson.url_enabled = False

If ckanext.datajsonld.path is omitted, it defaults to replacing ".json" in your
ckanext.datajson.path path with ".jsonld", so it probably won't need to be
specified.

The option ckanext.datajsonld.id is the @id value used to identify the data
catalog itself. If not given, it defaults to ckan.site_url.

You can specify which export map file to use to generates the data.json

    ckanext.datajson.export_map_filename = export.map.json

There are three map files available in folder [export_map](https://github.com/GSA/ckanext-datajson/tree/main/ckanext/datajson/export_map)
to choose from, or you can add you own in the same folder. By default, it looks
for file `export.map.json`, if not found, it defaults to
`export.catalog.map.sample.json`.


## Caching /data.json

If you're deploying inside Apache, some caching would be a good idea
because generating the /data.json file can take a good few moments.
Enable the cache modules:

	a2enmod cache
	a2enmod disk_cache

And then in your Apache configuration add:

	CacheEnable disk /data.json
	CacheRoot /tmp/apache_cache
	CacheDefaultExpire 120
	CacheMaxFileSize 50000000
	CacheIgnoreCacheControl On
	CacheIgnoreNoLastMod On
	CacheStoreNoStore On

And be sure to create /tmp/apache_cache and make it writable by the Apache process.


## Generating /data.json Off-Line

Generating this file is a little slow, so an alternative instead of caching is
to generate the file periodically (e.g. in a cron job). In that case, you'll want
to change the path that CKAN generates the file at to something *other* than /data.json.
In your CKAN .ini file, in the app:main section, add:

	ckanext.datajson.path = /internal/data.json

Now create a crontab file ("mycrontab") to download this URL to a file on disk
every ten minutes:

	0-59/10 * * * * wget -qO /path/to/static/data.json http://localhost/internal/data.json

And activate your crontab like so:

	crontab mycrontab

In Apache, we'll want to block outside access to the "internal" URL, and also
map the URL /data.json to the static file. In your httpd.conf, add:

	Alias /data.json /path/to/static/data.json
	
	<Location /internal/>
		Order deny,allow
		Allow from 127.0.0.1
		Deny from all
	</Location>

And then restart Apache. Wait for the cron job to run once, then check if
/data.json loads (and it should be fast!). Also double check that
http://yourdomain.com/internal/data.json gives a 403 forbidden error when
accessed from some other location.
