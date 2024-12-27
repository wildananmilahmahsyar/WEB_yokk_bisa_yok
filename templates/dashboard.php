<?php
function fetchPelanggaranFromFlask() {
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

$pelanggaran_list = fetchPelanggaranFromFlask();

// Hitung data untuk cards
$hari_ini = 0;
$minggu_ini = 0;
$bulan_ini = 0;
$total_bulanan = array_fill(1, 12, 0); // Array untuk chart (12 bulan)

foreach ($pelanggaran_list as $pelanggar) {
    $waktu = strtotime($pelanggar['time']);
    $tanggal = date("Y-m-d", $waktu);
    $bulan = (int)date("m", $waktu);
    $tahun = date("Y", $waktu);

    if ($tanggal == date("Y-m-d")) $hari_ini++;
    if ($waktu >= strtotime("-7 days")) $minggu_ini++;
    if ($bulan == date("m")) $bulan_ini++;
    $total_bulanan[$bulan]++;
}
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="../static/style/navbar.css">
    <link rel="stylesheet" href="../static/style/dashboard.css">
</head>
<body>
    <?php include 'sidenavbar.php'; ?>

    <div class="main-content" style="margin-top: 7%;">
        <div class="container_baris1">
            <div class="card_harian">
                <h1>Hari Ini</h1>
                <h1><?= $hari_ini ?></h1>
            </div>
            <div class="card_mingguan">
                <h1>Minggu Ini</h1>
                <h1><?= $minggu_ini ?></h1>
            </div>
        </div>

        <div class="container_baris2">
            <div class="card_bulanan">
                <h1>Bulan Ini</h1>
                <h1><?= $bulan_ini ?></h1>
            </div>
            <div class="card_tertindak">
                <h1>Tertindak</h1>
                <h1><?= count($pelanggaran_list) ?></h1>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="myChart"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
                datasets: [{
                    label: ' Pelanggaran per Tahun',
                    data: <?= json_encode(array_values($total_bulanan)) ?>,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    title: { display: true, text: ' Pelanggaran (per tahun)' }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    </script>
</body>
</html>
