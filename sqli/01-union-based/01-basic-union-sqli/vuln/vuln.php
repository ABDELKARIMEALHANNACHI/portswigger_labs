
<?php

$pdo = new PDO('sqlite:store.db');

$category = $_GET['category'] ?? '';

$query = "
    SELECT id, name, price
    FROM products
    WHERE category = '$category'
";

echo "<pre>DEBUG SQL: " . htmlspecialchars($query) . "</pre>";

$result = $pdo->query($query);

echo "<h1>Products</h1>";

foreach ($result as $row) {

    echo "<div>";
    echo "<b>" . htmlspecialchars($row['name']) . "</b><br>";
    echo "Price: $" . htmlspecialchars($row['price']);
    echo "</div><hr>";
}
?>

