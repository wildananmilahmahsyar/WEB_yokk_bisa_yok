<?php
session_start();  // Mulai sesi PHP

// Ambil user_id dari URL jika ada, atau gunakan dari sesi jika tersedia
$user_id = filter_input(INPUT_GET, 'user_id', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
if ($user_id) {
    $_SESSION['user_id'] = $user_id;
} elseif (isset($_SESSION['user_id'])) {
    $user_id = $_SESSION['user_id'];
} else {
    $user_name = "User tidak ditemukan";
    exit;
}

$url = "http://localhost:5000/get_user?user_id=$user_id";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

// Eksekusi permintaan dan ambil respons
$response = curl_exec($ch);
curl_close($ch);

// Decode JSON respons menjadi array PHP
$user_data = json_decode($response, true);

if (!isset($user_data['error'])) {
    $user_name = $user_data["nama"];
} else {
    $user_name = "User tidak ditemukan";
    
}

$current_page = basename($_SERVER['PHP_SELF']);
?>
 


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../static/style/navbar.css">
</head>
<body>
<div class="topbar">
        <div class="topbar-left">
            <img src="../static/gambar/favicon.png" alt="Logo" class="logo">

            <div class="search-container">
    <form method="POST" action="">
        <input 
            type="text" 
            name="search_query" 
            id="searchBar" 
            placeholder="Search by No Kendaraan..." 
            value="<?php echo htmlspecialchars($_POST['search_query'] ?? '') ?>" 
            autocomplete="off"
            oninput="this.form.submit()"
        >
    </form>

    <?php
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['search_query'])) {
        // Ambil query dari input user
        $query = filter_input(INPUT_POST, 'search_query', FILTER_SANITIZE_FULL_SPECIAL_CHARS);

        // URL untuk endpoint Flask
        $url = "http://127.0.0.1:5000/get_suggestions?query=" . urlencode($query);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);

        $data = json_decode($response, true);

        if (!empty($data['results'])) {
            echo '<div id="suggestions" class="suggestions">';
            foreach ($data['results'] as $result) {
                echo '<div><a href="search_result.php?no_kendaraan=' . urlencode($result['no_kendaraan']) . '">' . htmlspecialchars($result['no_kendaraan']) . '</a></div>';
            }
            echo '</div>';
        } else {
            echo '<div id="suggestions" class="suggestions"><div>No results found</div></div>';
        }
    }
    ?>
</div>



            
                                        
                <div class="navbar">
                    <ul class="navbar-list">
                        <li class="navbar-item"><a href="dashboard.php" class="navbar-link">Dashboard</a></li>
                        <li class="navbar-item"><a href="Daftarpelanggar.php" class="navbar-link">Daftarpelanggar</a></li>
                        <li class="navbar-item"><a href="arsip.php" class="navbar-link">Arsip</a></li>
                        
                    </ul>
                </div>
        </div>
        <div class="topbar-right">
            <div class="dropdown">
                <p class="profile-name"><?php echo htmlspecialchars($user_name); ?></p>
                <div class="dropdown-content">
                    <a href="profile.php">Profile</a>
                    <a href="http://localhost:5000/logout">Log Out</a>
                </div>
            </div>
        </div>
    </div>

    
</body>
<script>
document.addEventListener("DOMContentLoaded", function() {
    const currentPath = window.location.pathname.split("/").pop();
    const navLinks = document.querySelectorAll(".topbar a");

    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
});

function handleKeyPress(event) {
        if (event.key === 'Enter') {
            searchNoKendaraan();
        }
    }

    function searchNoKendaraan() {
        const noKendaraan = document.getElementById("searchBar").value;
        if (noKendaraan) {
            window.location.href = `search_result.php?no_kendaraan=${encodeURIComponent(noKendaraan)}`;
        }
    }

    
</script>
</html>
