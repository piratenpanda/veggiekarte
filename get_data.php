
<?php

// Overpass API URL

$url = 'http://overpass-api.de/api/interpreter';

// Retrieves all nodes with diet:vegan tags in Germany only atm

$data = '<?xml version="1.0" encoding="UTF-8"?>
<osm-script output="json" timeout="900">
  <union>
    <query type="node">
      <has-kv k="diet:vegan"/>
      <bbox-query e="14.97" n="54.87" s="47.36" w="5.87" />
    </query>
    <query type="way">
      <has-kv k="diet:vegan"/>
      <bbox-query e="14.97" n="54.87" s="47.36" w="5.87" />
    </query>
    <query type="relation">
      <has-kv k="diet:vegan"/>
      <bbox-query e="14.97" n="54.87" s="47.36" w="5.87" />
    </query>
  </union>
  <print mode="body"/>
  <recurse type="down"/>
  <print mode="skeleton"/>
</osm-script>';

// Send data request via curl

$ch = curl_init();

curl_setopt($ch,CURLOPT_URL, $url);
curl_setopt($ch,CURLOPT_POST, count($data));
curl_setopt($ch,CURLOPT_POSTFIELDS, $data);

//execute post

$result = curl_exec($ch);

//close connection

curl_close($ch);


?>
