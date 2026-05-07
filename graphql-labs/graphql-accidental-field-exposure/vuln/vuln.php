<?php
/**
 * VULNERABLE: password and role fields in GraphQL schema.
 * Introspection reveals them; resolvers return raw DB row.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$users = [
    1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','password'=>'supersecret123','role'=>'ADMIN'],
    2 => ['id'=>2,'username'=>'carlos','email'=>'carlos@corp.com','password'=>'hunter2','role'=>'USER'],
];

$userType = new ObjectType([
    'name' => 'User',
    'fields' => [
        'id'       => ['type' => Type::int()],
        'username' => ['type' => Type::string()],
        'email'    => ['type' => Type::string()],
        'password' => ['type' => Type::string()],  // VULN
        'role'     => ['type' => Type::string()],  // VULN
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getUser' => [
            'type' => $userType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => fn($r,$args) => $users[$args['id']] ?? null,
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
