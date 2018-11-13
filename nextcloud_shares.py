#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the amount shares to and from the specified nextcloud instance
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


class NextcloudShares:
	def config(self):
		config = {
			'shares': [
				'graph_title Nextcloud Shares',
				'graph_args --base 1000 -l 0',
				'graph_vlabel number of shares',
				'graph_info graph showing the number of shares',
				'graph_category nextcloud',
				'num_fed_shares_received.label federated shares recieved',
				'num_fed_shares_received.info current total of federated shares recieved',
				'num_fed_shares_received.min 0',
				'num_fed_shares_sent.label federated shares sent',
				'num_fed_shares_sent.info current total of federated shares sent',
				'num_fed_shares_sent.min 0',
				'num_shares.label total number of shares',
				'num_shares.info current over all total of shares',
				'num_shares.min 0',
				'num_shares_groups.label group shares',
				'num_shares_groups.info current total of group shares',
				'num_shares_groups.min 0',
				'num_shares_link.label link shares',
				'num_shares_link.info current total of shares through a link',
				'num_shares_link.min 0',
				'num_shares_link_no_password.label link shares without a password',
				'num_shares_link_no_password.info current total of shares through a link without a password protection',
				'num_shares_link_no_password.min 0',
				'num_shares_user.label user shares',
				'num_shares_user.info current total of user shares',
				'num_shares_user.min 0'
			]
		}

		return config

	def get_data(self, api_response):
		data = {
			'nextcloud_shares': [],
		}

		# shares
		shares = api_response['ocs']['data']['nextcloud']['shares']
		data['nextcloud_shares'].append('multigraph nextcloud_shares')

		# append for every key in shares the key and the value if the key starts with "num"
		[data['nextcloud_shares'].append(str(key) + ".value " + str(shares[key]))
			for key in shares if key.startswith('num')]

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
	NextcloudShares().main()
