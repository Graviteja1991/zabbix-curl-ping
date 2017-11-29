#!/usr/bin/env python
import os
import tempfile
import subprocess
import json
import logging
import argparse


def shell(cmd, expected_exit_code=0, stdin=None, stdout=None, stderr=None, capture=True, show_cmd=True):
    if show_cmd:
        print cmd
    captured = None
    captured_prefix = 'captured.%s.' % os.getpid()

    if capture:
        captured = tempfile.TemporaryFile(prefix=captured_prefix, mode='w+b')
        exit_code = subprocess.call(cmd, stdout=captured, stderr=captured, stdin=stdin, shell=True)
    else:
        exit_code = subprocess.call(cmd, stdout=stdout, stderr=stderr, stdin=stdin, shell=True)

    try:
        if exit_code not in expected_exit_code:
            raise RuntimeError('%s exit code = %s', (cmd, exit_code))
    except TypeError:
        if exit_code != expected_exit_code:
            raise RuntimeError('%s exit code = %s', (cmd, exit_code))

    if capture:
        return captured.read()


def discovery(options):
    discovery_out = {"data": []}
    for item_name in options.discovery_items:
        discovery_out["data"].append({"{#CURL_PARAMS}": options.curl_params, "{#ITEM_NAME}": item_name})
    print json.dumps(discovery_out)


def check_curl(options):
    try:
        result = {}

        for i in xrange(int(options.measurement_count)):
            json_out = {}
            for item_name in options.discovery_items:
                json_out[item_name] = '%{' + item_name + '}'

            json_out = json.loads(shell("curl -s -w '{json_out}' -o /dev/null {curl_params}".format(
                json_out=json.dumps(json_out),
                curl_params=options.curl_params,
            ), capture=True, show_cmd=options.dry_run))

            for item_name in options.discovery_items:
                if item_name not in result or result[item_name] < float(json_out[item_name].replace(',','.')):
                    result[item_name] = float(json_out[item_name].replace(',','.'))

        for item_name in options.discovery_items:
            cmd = 'zabbix_sender -c {zabbix_config} --key "{key}" --value {value}'.format(
                zabbix_config=options.zabbix_config,
                key="zabbix_curl_check[{curl_params},{item_name}]".format(
                    curl_params=options.curl_params,
                    item_name=item_name,
                ),
                value=result[item_name]
            )
            if options.dry_run:
                print cmd
            else:
                shell(cmd, show_cmd=False, capture=True)

        print '1'
    except (RuntimeError, KeyError, ValueError):
        print '0'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--discovery", type=bool, default=False,
        help="Return LLD discovery JSON for create Zabbix Tapper items and Triggers",
    )
    parser.add_argument(
        "--discovery-items", type=str,
        default="time_total,time_namelookup,time_connect,time_pretransfer,time_starttransfer,size_download,http_code",
        help="Comma separated list LLD {#ITEM_NAME}, see man curl for --write-out args",
   )
    parser.add_argument(
        "--curl-params", type=str, default='--connect-timeout=10 https://google.com',
        help="CURL params for check server",
    )

    parser.add_argument(
        "--zabbix-config", type=str, default="/etc/zabbix/zabbix_agentd.conf",
        help="ZABBIX config file for zabbix_sender",
    )

    parser.add_argument(
        "--measurement-count", type=int, default=3, help="How many time run curl with --curl-params",
    )

    parser.add_argument(
        "--dry-run", type=bool, default=False, help="Don't run zabbix-sender for measurement",
    )

    args = parser.parse_args()
    args.discovery_items = [o.strip() for o in str(args.discovery_items).split(",")]

    if args.discovery:
        discovery(args)
    else:
        check_curl(args)
