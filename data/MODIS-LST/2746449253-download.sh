#!/bin/bash

GREP_OPTIONS=''

cookiejar=$(mktemp cookies.XXXXXXXXXX)
netrc=$(mktemp netrc.XXXXXXXXXX)
chmod 0600 "$cookiejar" "$netrc"
function finish {
  rm -rf "$cookiejar" "$netrc"
}

trap finish EXIT
WGETRC="$wgetrc"

prompt_credentials() {
    echo "Enter your Earthdata Login or other provider supplied credentials"
    read -p "Username (jirvingphd): " username
    username=${username:-jirvingphd}
    read -s -p "Password: " password
    echo "machine urs.earthdata.nasa.gov login $username password $password" >> $netrc
    echo
}

exit_with_error() {
    echo
    echo "Unable to Retrieve Data"
    echo
    echo $1
    echo
    echo "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023145.h09v06.061.2023154043201/MOD11A2.A2023145.h09v06.061.2023154043201.hdf"
    echo
    exit 1
}

prompt_credentials
  detect_app_approval() {
    approved=`curl -s -b "$cookiejar" -c "$cookiejar" -L --max-redirs 5 --netrc-file "$netrc" https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023145.h09v06.061.2023154043201/MOD11A2.A2023145.h09v06.061.2023154043201.hdf -w '\n%{http_code}' | tail  -1`
    if [ "$approved" -ne "200" ] && [ "$approved" -ne "301" ] && [ "$approved" -ne "302" ]; then
        # User didn't approve the app. Direct users to approve the app in URS
        exit_with_error "Please ensure that you have authorized the remote application by visiting the link below "
    fi
}

setup_auth_curl() {
    # Firstly, check if it require URS authentication
    status=$(curl -s -z "$(date)" -w '\n%{http_code}' https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023145.h09v06.061.2023154043201/MOD11A2.A2023145.h09v06.061.2023154043201.hdf | tail -1)
    if [[ "$status" -ne "200" && "$status" -ne "304" ]]; then
        # URS authentication is required. Now further check if the application/remote service is approved.
        detect_app_approval
    fi
}

setup_auth_wget() {
    # The safest way to auth via curl is netrc. Note: there's no checking or feedback
    # if login is unsuccessful
    touch ~/.netrc
    chmod 0600 ~/.netrc
    credentials=$(grep 'machine urs.earthdata.nasa.gov' ~/.netrc)
    if [ -z "$credentials" ]; then
        cat "$netrc" >> ~/.netrc
    fi
}

fetch_urls() {
  if command -v curl >/dev/null 2>&1; then
      setup_auth_curl
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        curl -f -b "$cookiejar" -c "$cookiejar" -L --netrc-file "$netrc" -g -o $stripped_query_params -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  elif command -v wget >/dev/null 2>&1; then
      # We can't use wget to poke provider server to get info whether or not URS was integrated without download at least one of the files.
      echo
      echo "WARNING: Can't find curl, use wget instead."
      echo "WARNING: Script may not correctly identify Earthdata Login integrations."
      echo
      setup_auth_wget
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        wget --load-cookies "$cookiejar" --save-cookies "$cookiejar" --output-document $stripped_query_params --keep-session-cookies -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  else
      exit_with_error "Error: Could not find a command-line downloader.  Please install curl or wget"
  fi
}

fetch_urls <<'EDSCEOF'
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023145.h09v06.061.2023154043201/MOD11A2.A2023145.h09v06.061.2023154043201.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023145.h09v05.061.2023154041457/MOD11A2.A2023145.h09v05.061.2023154041457.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023153.h09v06.061.2023164032102/MOD11A2.A2023153.h09v06.061.2023164032102.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023153.h09v05.061.2023164034529/MOD11A2.A2023153.h09v05.061.2023164034529.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023161.h09v06.061.2023170174522/MOD11A2.A2023161.h09v06.061.2023170174522.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023161.h09v05.061.2023170174847/MOD11A2.A2023161.h09v05.061.2023170174847.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023169.h09v06.061.2023178032028/MOD11A2.A2023169.h09v06.061.2023178032028.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023169.h09v05.061.2023178033518/MOD11A2.A2023169.h09v05.061.2023178033518.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023177.h09v06.061.2023191223224/MOD11A2.A2023177.h09v06.061.2023191223224.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023177.h09v05.061.2023191223728/MOD11A2.A2023177.h09v05.061.2023191223728.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023185.h09v05.061.2023201061553/MOD11A2.A2023185.h09v05.061.2023201061553.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023185.h09v06.061.2023201095900/MOD11A2.A2023185.h09v06.061.2023201095900.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023193.h09v05.061.2023214104254/MOD11A2.A2023193.h09v05.061.2023214104254.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023193.h09v06.061.2023214104850/MOD11A2.A2023193.h09v06.061.2023214104850.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023201.h09v06.061.2023215145515/MOD11A2.A2023201.h09v06.061.2023215145515.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023201.h09v05.061.2023215145934/MOD11A2.A2023201.h09v05.061.2023215145934.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023209.h09v06.061.2023220022032/MOD11A2.A2023209.h09v06.061.2023220022032.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023209.h09v05.061.2023220022857/MOD11A2.A2023209.h09v05.061.2023220022857.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023217.h09v06.061.2023226040517/MOD11A2.A2023217.h09v06.061.2023226040517.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023217.h09v05.061.2023226041049/MOD11A2.A2023217.h09v05.061.2023226041049.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023225.h09v06.061.2023235042835/MOD11A2.A2023225.h09v06.061.2023235042835.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023225.h09v05.061.2023235043337/MOD11A2.A2023225.h09v05.061.2023235043337.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023233.h09v05.061.2023242040454/MOD11A2.A2023233.h09v05.061.2023242040454.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023233.h09v06.061.2023242040015/MOD11A2.A2023233.h09v06.061.2023242040015.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023241.h09v06.061.2023251215934/MOD11A2.A2023241.h09v06.061.2023251215934.hdf
https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/MOD11A2.061/MOD11A2.A2023241.h09v05.061.2023251220940/MOD11A2.A2023241.h09v05.061.2023251220940.hdf
EDSCEOF