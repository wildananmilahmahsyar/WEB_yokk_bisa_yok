<?php
if (!isset($_GET['no_kendaraan'])) {
    echo "No Kendaraan tidak ditemukan.";
    exit;
}

$no_kendaraan = urlencode($_GET['no_kendaraan']);

// Komunikasi ke Flask server untuk mendapatkan detail
$url = "http://127.0.0.1:5000/get_detail/$no_kendaraan";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);

if (isset($data['error'])) {
    echo "<p>Data tidak ditemukan.</p>";
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hasil Pencarian</title>
    <link rel="stylesheet" href="../static/style/navbar.css">
</head>
<body>
    <?php include 'sidenavbar.php'; ?>
    <div class="main-content">
        <h1>Hasil Pencarian untuk No Kendaraan: <?= htmlspecialchars($_GET['no_kendaraan']) ?></h1>
        <table border="1" cellpadding="10" cellspacing="0">
            <tr><td>Nama:</td><td><?= htmlspecialchars($data['nama'] ?? '-') ?></td></tr>
            <tr><td>No HP:</td><td><?= htmlspecialchars($data['no_hp'] ?? '-') ?></td></tr>
            <tr><td>Nomor SIM:</td><td><?= htmlspecialchars($data['no_sim'] ?? '-') ?></td></tr>
            <tr><td>Alamat:</td><td><?= htmlspecialchars($data['alamat'] ?? '-') ?></td></tr>
            <tr><td>Nomor Kendaraan:</td><td><?= htmlspecialchars($data['no_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Jenis Kendaraan:</td><td><?= htmlspecialchars($data['jenis_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Warna Kendaraan:</td><td><?= htmlspecialchars($data['warna_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Status:</td><td><?= htmlspecialchars($data['status'] ?? '-') ?></td></tr>
        </table>
    </div>
</body>
</html>
