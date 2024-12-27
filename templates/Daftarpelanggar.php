<?php
function fetchDataFromFlask() {
    $flask_url = "http://127.0.0.1:5000/get_realtime_pelanggar";
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $flask_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        curl_close($ch);
        return [];
    }
    curl_close($ch);
    return json_decode($response, true)["data"] ?? [];
}

// Ambil data awal dari Flask
$pelanggar_list = fetchDataFromFlask();
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daftar Pelanggar</title>
    <link rel="stylesheet" href="../static/style/navbar.css">
    <link rel="stylesheet" href="../static/style/Daftarpelanggar.css">
</head>

<body>
    
    <?php include 'sidenavbar.php'; ?>

    <div class="main-content">
        <h1>Daftar Pelanggar</h1>
        <table>
            <thead>
                <tr>
                    <th>Plat Kendaraan</th>
                    <th>Lokasi</th>
                    <th>Status</th>
                    <th>Waktu</th>
                    <th>Aksi</th>
                </tr>
            </thead>
            <tbody id="pelanggar-table-body">
            <?php foreach ($pelanggar_list as $pelanggar): ?>
                <tr>
                    <td><?= htmlspecialchars($pelanggar['no_kendaraan']) ?></td>
                    <td><?= htmlspecialchars($pelanggar['location']) ?></td>
                    <td><?= htmlspecialchars($pelanggar['status'] ?? 'Menunggu') ?></td>
                    <td><?= htmlspecialchars($pelanggar['time']) ?></td>
                    <td>
                        <form action="detail.php" method="GET">
                            <input type="hidden" name="no_kendaraan" value="<?= htmlspecialchars($pelanggar['no_kendaraan']) ?>">
                            <button type="submit" class="btn-link">Detail</button>
                        </form>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>

<!-- Script untuk Refresh Data Secara Real-Time -->
<script>
    function refreshData() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "reload_data.php", true);
        xhr.onload = function () {
            if (xhr.status === 200) {
                document.getElementById("pelanggar-table-body").innerHTML = xhr.responseText;
            }
        };
        xhr.send();
    }

    setInterval(refreshData, 5000);
</script>
</html>
