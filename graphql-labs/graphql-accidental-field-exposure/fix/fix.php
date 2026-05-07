<?php
/**
 * FIX:
 * 1. Separate public UserPublic DTO — password/role NOT in schema.
 * 2. Introspection blocked via middleware check.
 * 3. Resolver returns only safe fields.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$users = [
    1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','_password'=>'hash','_role'=>'ADMIN'],
    2 => ['id'=>2,'username'=>'carlos','email'=>'carlos@corp.com','_password'=>'hash','_role'=>'USER'],
];

// FIX: public-safe type — no password, no role
$userPublicType = new ObjectType([
    'name' => 'UserPublic',
    'fields' => [
        'id'       => ['type' => Type::int()],
        'username' => ['type' => Type::string()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getUser' => [
            'type' => $userPublicType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => function($r, $args) use ($users) {
                $u = $users[$args['id']] ?? null;
                return $u ? ['id'=>$u['id'],'username'=>$u['username']] : null;
            }
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);

// FIX: block introspection
if (str_contains($input['query'] ?? '', '__schema') || str_contains($input['query'] ?? '', '__type')) {
    http_response_code(403);
    echo json_encode(['errors'=>[['message'=>'Introspection disabled']]]);
    exit;
}

$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
