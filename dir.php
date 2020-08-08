<?php
$out = array();
foreach (glob('data/*.json') as $filename) {
    $p = pathinfo($filename);
    $out[] = $p['filename'];
}
echo json_encode($out)
?>
