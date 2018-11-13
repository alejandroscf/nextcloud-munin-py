#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the amount of users sucessfully logging in to the specified nextcloud instance
#
# Parameters understood:
#     config   (required)
#     autoconf (optional - used by munin-config)

# Magic markers - optional - used by installation scripts and
# munin-config:
#
#  #%# family=manual
#  #%# capabilities=autoconf
import requests
import sys
import os


class NextcloudUsers:
	def config(self):
		config = {
			'users': [
				'graph_title Nextcloud User Activity',
				'graph_args --base 1000 -l 0',
				'graph_printf %.0lf',
				'graph_vlabel connected users',
				'graph_info graph showing the number of connected user',
				'graph_category nextcloud',
				'last5minutes.label last 5 minutes',
				'last5minutes.info users connected in the last 5 minutes',
				'last5minutes.min 0',
				'last1hour.label last hour',
				'last1hour.info users connected in the last hour',
				'last1hour.min 0',
				'last24hours.label last 24 hours',
				'last24hours.info users connected in the last 24 hours',
				'last24hours.min 0',
				'num_users.label number of users',
				'num_users.info total number of users',
				'num_users.min 0'
			]
		}

		return config

	def get_data(self, api_response):
		data = {
			'nextcloud_users': [],
		}
		# users
		users = api_response['ocs']['data']['activeUsers']
		num_users = api_response['ocs']['data']['nextcloud']['storage']['num_users']

		# append for every key in users the key and the value to the results
		[data['nextcloud_users'].append(str(key) + ".value " + str(users[key]))
			for key in users.keys()]

		# append total number of users
		data['nextcloud_users'].append('num_users.value %s' % num_users)

		return data

	def run(self):
		# init request session with specific header and credentials
		with requests.Session() as s:
			# read credentials from env
			s.auth = (os.environ.get('username'), os.environ.get('password'))

			# update header for json
			s.headers.update({'Accept': 'application/json'})

			# request the data
			r = s.get(os.environ.get('url'))

		# if status code is successful continue
		if r.status_code == 200:
			result = self.get_data(r.json())

			# for key in results print every entry in dict
			[print('\n'.join(result[key])) for key in result.keys()]

		elif r.status_code == 996:
			print('server error')
		elif r.status_code == 997:
			print('not authorized')
		elif r.status_code == 998:
			print('not found')
		else:
			print('unknown error')

	def main(self):
		# check if any argument is given
		if sys.argv.__len__() >= 2:
			# check if first argument is config or autoconf if not fetch data
			if sys.argv[1] == "config":
				# for key in config().keys() print every entry in dict
				[print('\n'.join(self.config()[key])) for key in self.config().keys()]
				if os.environ.get('MUNIN_CAP_DIRTYCONFIG') == '1':
					self.run()
			elif sys.argv[1] == 'autoconf':
				if None in [os.environ.get('username'), os.environ.get('password')]:
					print('env variables are missing')
				else:
					print('yes')
		else:
			self.run()


if __name__ == "__main__":
	NextcloudUsers().main()
