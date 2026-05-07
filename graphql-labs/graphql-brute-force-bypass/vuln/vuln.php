<?php
/**
 * VULNERABLE: Login mutation — rate limit per HTTP request only.
 * Alias batching sends N attempts in 1 request → bypass.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

$users = ['carlos' => 'abc123', 'admin' => 'password123'];

// Simple in-memory rate limiter (per IP, per request — vulnerable)
$requestCount = 0; // In real app: Redis counter

$loginResultType = new ObjectType(['name'=>'LoginResult','fields'=>[
    'success' => ['type'=>Type::boolean()],
    'token'   => ['type'=>Type::string()],
    'message' => ['type'=>Type::string()],
]]);

$queryType    = new ObjectType(['name'=>'Query','fields'=>['dummy'=>['type'=>Type::boolean(),'resolve'=>fn()=>true]]]);
$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'login' => [
        'type' => $loginResultType,
        'args' => [
            'username' => ['type' => Type::nonNull(Type::string())],
            'password' => ['type' => Type::nonNull(Type::string())],
        ],
        // VULN: rate limit not checked per-alias, only per HTTP request
        'resolve' => function($r, $args) use ($users) {
            if (($users[$args['username']] ?? null) === $args['password']) {
                return ['success'=>true,'token'=>'jwt-for-'.$args['username'],'message'=>'OK'];
            }
            return ['success'=>false,'token'=>null,'message'=>'Invalid credentials'];
        }
    ],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
