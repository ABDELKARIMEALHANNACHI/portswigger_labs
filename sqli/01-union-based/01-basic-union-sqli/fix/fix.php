
<?php

$pdo = new PDO('sqlite:store.db');

$category = $_GET['category'] ?? '';

$stmt = $pdo->prepare("
    SELECT id,name,price
    FROM products
    WHERE category = ?
");

$stmt->execute([$category]);

foreach ($stmt as $row) {

    echo htmlspecialchars($row['name']);
}
?>

