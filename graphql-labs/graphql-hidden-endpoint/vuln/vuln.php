<?php
/**
 * VULNERABLE: GraphQL at obscured path.
 * Introspection enabled. Mutations unauthenticated.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\{ObjectType, Type, NonNull};

$users = [1 => ['id'=>1,'username'=>'admin','email'=>'admin@corp.com','isAdmin'=>true]];

$userType = new ObjectType(['name'=>'User','fields'=>[
    'id'=>['type'=>Type::int()],
    'username'=>['type'=>Type::string()],
    'email'=>['type'=>Type::string()],
    'isAdmin'=>['type'=>Type::boolean()],
]]);

$queryType = new ObjectType(['name'=>'Query','fields'=>[
    'getUser'=>['type'=>$userType,'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>fn($r,$args) => $users[$args['id']] ?? null],
]]);

$mutationType = new ObjectType(['name'=>'Mutation','fields'=>[
    'deleteUser'=>['type'=>Type::boolean(),'args'=>['id'=>['type'=>Type::nonNull(Type::int())]],
        'resolve'=>function($r,$args) use (&$users){ $e=isset($users[$args['id']]); unset($users[$args['id']]); return $e; }],
    'changeEmail'=>['type'=>$userType,'args'=>[
        'id'=>['type'=>Type::nonNull(Type::int())],
        'email'=>['type'=>Type::nonNull(Type::string())]],
        'resolve'=>function($r,$args) use (&$users){
            if(isset($users[$args['id']])){ $users[$args['id']]['email']=$args['email']; return $users[$args['id']]; }
            return null;
        }],
]]);

$schema = new Schema(['query'=>$queryType,'mutation'=>$mutationType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query'] ?? '');
header('Content-Type: application/json');
echo json_encode($result->toArray());
