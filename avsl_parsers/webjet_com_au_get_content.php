<?php

try {

$args = NULL;
function request_args() {
	global $args;
	if ($args === NULL) {
		$args = array_slice($_SERVER['argv'], 1);
		$args = implode('&', $args);
	}
	return $args;
}

/* функция парсинга кук */

function _coo($r) {
$h=explode("\n", $r);
$coo=array();
foreach ($h as $l) {
	$p=strpos($l, ':');
	if ($p===FALSE) continue;
	$key = substr($l,0,$p);
	if ($key==='Set-Cookie') {
		$value = trim(substr($l,$p+1));
		$p=strpos($value, ';');
		if ($p===FALSE) {
			$coo[]=$value;
		} else {
			$coo[]=substr($value,0,$p);
		}	

		if (count($coo) === 2) break;
	}
}

//var_dump($coo);

return "OX_plg=swf,qt,wmp,shk; " . implode("; ", $coo);
}



/* получаем куки */

$url="http://tsa.webjet.com.au/webjettsa/home.aspx?" . request_args();

$ch = curl_init($url);
$options = array(
CURLOPT_RETURNTRANSFER=>1,
CURLOPT_USERAGENT=>'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
CURLOPT_TIMEOUT=>30,
CURLOPT_FOLLOWLOCATION=>1,
CURLOPT_HEADER=>1,
CURLOPT_NOBODY=>1,
);
curl_setopt_array($ch, $options);
$r = curl_exec($ch);
if ($cn = curl_errno($ch))
throw new Exception("curl error #{$cn} with message \"" . curl_error($ch) . "\"");

$cookie=_coo($r);


$url="http://tsa.webjet.com.au/webjettsa/unauth.aspx?" . request_args();

$ch = curl_init($url);
$options = array(
CURLOPT_RETURNTRANSFER=>1,
CURLOPT_USERAGENT=>'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
CURLOPT_COOKIE=>$cookie,
CURLOPT_TIMEOUT=>30,
CURLOPT_FOLLOWLOCATION=>1,
CURLOPT_HEADER=>1,
CURLOPT_NOBODY=>0,
);
curl_setopt_array($ch, $options);
$r = curl_exec($ch);
if ($cn = curl_errno($ch))
throw new Exception("curl error #{$cn} with message \"" . curl_error($ch) . "\"");

/* продлеваем сессию */

$url="http://tsa.webjet.com.au/webjettsa/SessionExpired.aspx?mode=BookingPriceGuarantee";

$ch = curl_init($url);
$options = array(
CURLOPT_RETURNTRANSFER=>1,
CURLOPT_USERAGENT=>'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
CURLOPT_TIMEOUT=>30,
CURLOPT_FOLLOWLOCATION=>1,
CURLOPT_HEADER=>1,
CURLOPT_NOBODY=>1,
);
curl_setopt_array($ch, $options);
$r1 = curl_exec($ch);
if ($cn = curl_errno($ch))
throw new Exception("curl error #{$cn} with message \"" . curl_error($ch) . "\"");



preg_match('#name="__VIEWSTATE" id="__VIEWSTATE" value="([^"]+)" />#', $r, $m);

$zzz = $m[1];

$url = "http://tsa.webjet.com.au/webjettsa/unauth.aspx?" . request_args();

$ref = "http://tsa.webjet.com.au/webjettsa/unauth.aspx?" . request_args();

$ch = curl_init($url);
$options = array(
CURLOPT_RETURNTRANSFER=>1,
CURLOPT_USERAGENT=>'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
CURLOPT_REFERER => $ref,
CURLOPT_COOKIE => $cookie,
CURLOPT_TIMEOUT=>30,
CURLOPT_FOLLOWLOCATION=>1,
CURLOPT_HEADER=>1,
CURLOPT_NOBODY=>0,
CURLOPT_POST=>1,
CURLOPT_POSTFIELDS=>"__EVENTTARGET=ContentView%3APageLayout%3AProcessingSearch&__EVENTARGUMENT=FlightFinderTab&PFPageID=ProcessingSearch&PFLayoutID=Layout&__VIEWSTATE=" . urlencode($zzz),
);
curl_setopt_array($ch, $options);
$r = curl_exec($ch);

/* запрос на получение результата */

$url = 'http://tsa.webjet.com.au/webjettsa/Content/Flight/NewFlightResults/HybridFlightResults.aspx';

$ref = "http://tsa.webjet.com.au/webjettsa/unauth.aspx?" . request_args();

$ch = curl_init($url);
$options = array(
CURLOPT_RETURNTRANSFER=>1,
CURLOPT_USERAGENT=>'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
CURLOPT_REFERER => $ref,
CURLOPT_COOKIE => $cookie ."; LoadedFromServer=true;",
CURLOPT_TIMEOUT=>30,
CURLOPT_FOLLOWLOCATION=>1,
CURLOPT_HEADER=>1,
CURLOPT_NOBODY=>0,
);
curl_setopt_array($ch, $options);
$r = curl_exec($ch);
if ($cn = curl_errno($ch))
throw new Exception("curl error #{$cn} with message \"" . curl_error($ch) . "\"");

echo $r;

} catch(Exception $e) {

if ( 0 === strpos($e->getMessage(), 'curl error #28') )
    echo 'timeout';
else
    echo 'error';

}


