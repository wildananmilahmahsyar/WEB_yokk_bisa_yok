<?php
function fetchArsipFromFlask() {
    $flask_url = "http://127.0.0.1:5000/get_pelanggar_arsip";
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $flask_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo "cURL error: " . curl_error($ch);
        curl_close($ch);
        return [];
    }
    curl_close($ch);
    return json_decode($response, true)["data"] ?? [];
}

// Ambil data arsip dari Flask
$arsip_list = fetchArsipFromFlask();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arsip Pelanggar</title>
    <link rel="stylesheet" href="../static/style/navbar.css">
    <link rel="stylesheet" href="../static/style/Daftarpelanggar.css">
</head>
<body>
    <!-- Sidebar -->
    <?php include 'sidenavbar.php'; ?>

    <!-- Main Content -->
    <div class="main-content">
        <h1>Arsip Pelanggar</h1>
        <table>
        <thead>
    <tr>
        <th>Plat Kendaraan</th>
        <th>Lokasi</th>
        <th>Waktu</th>
        <th>Status</th>
        <th>Detail</th>
    </tr>
        </thead>
        <tbody>
            <?php if (!empty($arsip_list)): ?>
                <?php foreach ($arsip_list as $arsip): ?>
                    <tr>
                        <td><?= htmlspecialchars($arsip['no_kendaraan']) ?></td>
                        <td><?= htmlspecialchars($arsip['location']) ?></td>
                        <td><?= htmlspecialchars($arsip['time']) ?></td>
                        <td><?= htmlspecialchars($arsip['status'] ?? 'Tertindak') ?></td>
                        <td>
                            <a href="detailcopy.php?no_kendaraan=<?= urlencode($arsip['no_kendaraan']) ?>">Lihat Detail</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="5" style="text-align: center;">Tidak ada data arsip pelanggar.</td>
                </tr>
            <?php endif; ?>
        </tbody>

        </table>
    </div>
</body>
</html>
