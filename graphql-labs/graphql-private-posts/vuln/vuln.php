<?php
/**
 * VULNERABLE: GraphQL endpoint using webonyx/graphql-php
 * No auth check — private posts accessible by ID enumeration.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;

$posts = [
    1 => ['id'=>1,'title'=>'Welcome','content'=>'Hello world','postPassword'=>null,'isPublic'=>true],
    2 => ['id'=>2,'title'=>'Secret Draft','content'=>'Top secret','postPassword'=>'peter:Th3SecretPass!','isPublic'=>false],
];

$blogPostType = new ObjectType([
    'name' => 'BlogPost',
    'fields' => [
        'id'           => ['type' => Type::int()],
        'title'        => ['type' => Type::string()],
        'content'      => ['type' => Type::string()],
        'postPassword' => ['type' => Type::string()],  // VULN: exposed
        'isPublic'     => ['type' => Type::boolean()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getBlogPost' => [
            'type' => $blogPostType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            // VULN: no auth, no isPublic check
            'resolve' => fn($root, $args) => $posts[$args['id']] ?? null,
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
