<?php
/**
 * FIX:
 * 1. Only POST + application/json accepted.
 * 2. SameSite=Strict cookie.
 * 3. Custom CSRF header required.
 * 4. GET method returns 405.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

// FIX: reject non-POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['errors'=>[['message'=>'Method Not Allowed']]]);
    exit;
}

// FIX: enforce application/json (form-based CSRF uses form-urlencoded)
if (!str_contains($_SERVER['CONTENT_TYPE'] ?? '', 'application/json')) {
    http_response_code(415);
    echo json_encode(['errors'=>[['message'=>'Content-Type must be application/json']]]);
    exit;
}

// FIX: require custom header (triggers CORS preflight for cross-origin)
if (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') !== 'XMLHttpRequest') {
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Missing X-Requested-With header']]]);
    exit;
}

// FIX: SameSite=Strict cookie
setcookie('session', 'user-session-token', [
    'samesite' => 'Strict',
    'secure'   => true,
    'httponly' => true,
]);

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],'username'=>['type'=>Type::string()],'email'=>['type'=>Type::string()]
]]);
$queryType    = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>['email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            $users[1]['email']=$args['email']; return $users[1];
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
