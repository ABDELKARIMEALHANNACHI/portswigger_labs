<?php
/**
 * VULNERABLE: GraphQL accepts GET + form-encoded POST.
 * Attacker can host malicious HTML page that triggers mutations cross-origin.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

// VULN: SameSite=None cookie
setcookie('session', 'user-session-token', [
    'samesite' => 'None',
    'secure'   => true,
    'httponly' => true,
]);

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],'username'=>['type'=>Type::string()],'email'=>['type'=>Type::string()]
]]);
$queryType = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>['email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            $users[1]['email']=$args['email']; return $users[1]; // VULN: no CSRF check
        }],
    'deleteAccount'=>['type'=>Type::boolean(),'resolve'=>function($r,$a) use (&$users){
        $users=[]; return true;
    }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);

// VULN: accept GET and x-www-form-urlencoded
$query = '';
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $query = $_GET['query'] ?? '';
} elseif (str_contains($_SERVER['CONTENT_TYPE'] ?? '', 'application/x-www-form-urlencoded')) {
    $query = $_POST['query'] ?? '';
} else {
    $input = json_decode(file_get_contents('php://input'), true);
    $query = $input['query'] ?? '';
}

$result = GraphQL::executeQuery($schema, $query);
header('Content-Type: application/json');
echo json_encode($result->toArray());
