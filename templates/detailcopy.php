<?php
// Cek jika no_kendaraan tidak dikirim melalui URL
if (!isset($_GET['no_kendaraan'])) {
    echo "No Kendaraan tidak ditemukan.";
    exit;
}

$no_kendaraan = urlencode($_GET['no_kendaraan']);



// Ambil data detail dari Flask
$detail_url = "http://127.0.0.1:5000/get_detail/$no_kendaraan";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $detail_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);

if (isset($data['error'])) {
    echo "<p>Data tidak ditemukan.</p>";
    exit;
}

$photo_id = $data['photo_id'] ?? null;



// Handle tombol Hapus
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['delete'])) {
    $delete_url = "http://127.0.0.1:5000/deletearsip/" . urlencode($no_kendaraan);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $delete_url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE");
    curl_exec($ch);
    curl_close($ch);

    echo "<script>alert('Data berhasil dihapus.'); window.location.href = 'arsip.php';</script>";
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detail Pelanggaran</title>
    <link rel="stylesheet" href="../static/style/navbar.css">
    <link rel="stylesheet" href="../static/style/detail.css">
</head>
<body>
    <?php include 'sidenavbar.php'; ?>

    <!-- Main Content -->
    <div class="main-content">
        <img width="50" height="50" src="https://img.icons8.com/ios-filled/50/left.png" alt="left" onclick="history.back()">

        <div class="container_atas">
            <?php if ($photo_id): ?>
                <img src="https://drive.google.com/thumbnail?id=<?= htmlspecialchars($photo_id) ?>" alt="Foto Kendaraan" >
            <?php else: ?>
                <p style="color: red;">Foto kendaraan tidak tersedia.</p>
            <?php endif; ?>
        </div>

        <div class="data">
        <table style="width:100%">
            <tr><td>Nama:</td><td><?= htmlspecialchars($data['nama'] ?? '-') ?></td></tr>
            <tr><td>No Hp:</td><td><?= htmlspecialchars($data['no_hp'] ?? '-') ?></td></tr>
            <tr><td>Nomor SIM:</td><td><?= htmlspecialchars($data['no_sim'] ?? '-') ?></td></tr>
            <tr><td>Alamat:</td><td><?= htmlspecialchars($data['alamat'] ?? '-') ?></td></tr>
            <tr><td>Nomor Kendaraan:</td><td><?= htmlspecialchars($data['no_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Jenis Kendaraan:</td><td><?= htmlspecialchars($data['jenis_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Warna Kendaraan:</td><td><?= htmlspecialchars($data['warna_kendaraan'] ?? '-') ?></td></tr>
            <tr><td>Status:</td><td><?= htmlspecialchars($data['status'] ?? '-') ?></td></tr>
        </table>
        </div>

        <!-- Tombol Aksi Selalu Muncul -->
        <div class="button_container">

            <form method="POST" style="display: inline;">
                <input type="hidden" name="no_kendaraan" value="<?= htmlspecialchars($data['no_kendaraan'] ?? '') ?>">
                <button type="submit" name="delete" class="btn info">Hapus</button>
            </form>
        </div>
    </div>
</body>
</html>
