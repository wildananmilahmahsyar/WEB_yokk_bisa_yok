<?php
session_start();  // Mulai sesi PHP

// Ambil user_id dari parameter URL dan simpan di sesi jika tersedia
$user_id = filter_input(INPUT_GET, 'user_id', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
if ($user_id) {
    $_SESSION['user_id'] = $user_id;  // Perbarui sesi dengan user_id dari URL
} elseif (isset($_SESSION['user_id'])) {
    $user_id = $_SESSION['user_id'];  // Gunakan sesi jika tidak ada di URL
} else {
    echo "<p>User tidak ditemukan.</p>";
    exit;
}

$url = "http://localhost:5000/get_user?user_id=$user_id";  // Tambahkan user_id sebagai parameter

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

// Ambil respons dari Flask
$response = curl_exec($ch);

if (curl_errno($ch)) {
    echo "<p>Error: " . curl_error($ch) . "</p>";
    curl_close($ch);
    exit;
}

curl_close($ch);

// Decode JSON respons
$user_data = json_decode($response, true);

if (!isset($user_data['error'])) {
    $user_name = htmlspecialchars($user_data["nama"]);
    $nrp = htmlspecialchars($user_data["nrp"]);
    $no_hp = htmlspecialchars($user_data["no_hp"]);
    $email = htmlspecialchars($user_data["email"]);
} else {
    echo "<p>User tidak ditemukan.</p>";
    exit;
}
?>




<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="../static/gambar/favicon.png">
    <title>Profile</title>
    <link rel="stylesheet" href="../static/style/navbar.css">
    <link rel="stylesheet" href="../static/style/profile.css">
</head>
<body>
    <?php include 'sidenavbar.php'; ?>

    <div class="main-content">
        <div class="profile-container">
            <p class="profile-name"><?php echo $user_name; ?></p>
            <h2 class="title">OPERATOR E-TLE</h2>
            <div class="info">
                <p>Nama: <?php echo $user_name; ?></p>
                <p>NRP Petugas: <?php echo $nrp; ?></p>
                <p>No Hp: <?php echo $no_hp; ?></p>
                <p>Email: <?php echo $email; ?></p>
            </div>
            <!-- <button class="edit-button">Edit</button> -->
        </div>
    </div>
</body>
</html>
