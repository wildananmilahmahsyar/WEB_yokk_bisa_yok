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

$pelanggar_list = fetchDataFromFlask();

foreach ($pelanggar_list as $pelanggar): ?>
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
