<?php
/**
 * FIX: Per-attempt rate limit inside resolver using Redis.
 * Alias batching now triggers the limit per alias, not per request.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type};

// FIX: Redis-based per-user rate limiter
function checkRateLimit(string $username, string $ip): bool {
    // In production: use Redis INCR + EXPIRE
    // Simulated here with APCu or session
    $key = "login_attempts:{$ip}:{$username}";
    $attempts = apcu_fetch($key) ?: 0;
    if ($attempts >= 5) return false;
    apcu_store($key, $attempts + 1, 60); // 60-second window
    return true;
}

$users = ['carlos' => 'abc123', 'admin' => 'password123'];

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
        'resolve' => function($r, $args) use ($users) {
            $ip = $_SERVER['REMOTE_ADDR'];
            // FIX: check INSIDE resolver — alias batching now rate-limited correctly
            if (!checkRateLimit($args['username'], $ip)) {
                throw new \Exception('Too many attempts. Try again later.');
            }
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
