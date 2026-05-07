<?php
/**
 * FIX:
 * 1. Auth middleware for mutations.
 * 2. Introspection blocked.
 * 3. GET method disabled (prevents trivial URL-based probing).
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

function requireAuth(): void {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if ($auth !== 'Bearer valid-admin-token') {
        http_response_code(401);
        echo json_encode(['errors'=>[['message'=>'Unauthorized']]]);
        exit;
    }
}

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com']];

$userType = new ObjectType(['name'=>'UserPublic','fields'=>[
    'id'=>['type'=>Type::int()],
    'username'=>['type'=>Type::string()],
    'email'=>['type'=>Type::string()],
]]);

$queryType  = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$a) => $users[$a['id']] ?? null],
]]);

$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'changeEmail'=>['type'=>$userType,'args'=>[
        'id'=>['type'=>Type::nonNull(Type::int())],
        'email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            requireAuth(); // FIX
            if(isset($users[$args['id']])){ $users[$args['id']]['email']=$args['email']; return $users[$args['id']]; }
            return null;
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);

// FIX: block introspection
if(str_contains($input['query']??'','__schema')||str_contains($input['query']??'','__type')){
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Introspection disabled']]]);
    exit;
}

$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
