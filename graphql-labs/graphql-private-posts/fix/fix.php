<?php
/**
 * FIX: Authorization-aware resolver.
 * - Private posts returned only to authenticated admins.
 * - postPassword masked for non-admins.
 */
require 'vendor/autoload.php';

use GraphQL\GraphQL;
use GraphQL\Type\Schema;
use GraphQL\Type\Definition\ObjectType;
use GraphQL\Type\Definition\Type;
use GraphQL\Type\Definition\ResolveInfo;

$posts = [
    1 => ['id'=>1,'title'=>'Welcome','content'=>'Hello','postPassword'=>null,'isPublic'=>true],
    2 => ['id'=>2,'title'=>'Secret','content'=>'Top secret','postPassword'=>'peter:Th3SecretPass!','isPublic'=>false],
];

function getCurrentUser(): ?array {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    return $auth === 'Bearer admin-token' ? ['role'=>'admin'] : null;
}

$blogPostType = new ObjectType([
    'name'   => 'BlogPost',
    'fields' => [
        'id'      => ['type' => Type::int()],
        'title'   => ['type' => Type::string()],
        'content' => ['type' => Type::string()],
        // FIX: field-level resolver hides password from non-admins
        'postPassword' => [
            'type'    => Type::string(),
            'resolve' => function($post) {
                $user = getCurrentUser();
                return ($user && $user['role'] === 'admin') ? $post['postPassword'] : null;
            }
        ],
        'isPublic' => ['type' => Type::boolean()],
    ],
]);

$queryType = new ObjectType([
    'name' => 'Query',
    'fields' => [
        'getBlogPost' => [
            'type' => $blogPostType,
            'args' => ['id' => ['type' => Type::nonNull(Type::int())]],
            'resolve' => function($root, $args) use ($posts) {
                $post = $posts[$args['id']] ?? null;
                if (!$post) return null;
                $user = getCurrentUser();
                // FIX: block private post access for unauthenticated users
                if (!$post['isPublic'] && (!$user || $user['role'] !== 'admin')) {
                    return null;
                }
                return $post;
            }
        ],
    ],
]);

$schema = new Schema(['query' => $queryType]);
$input  = json_decode(file_get_contents('php://input'), true);
$result = GraphQL::executeQuery($schema, $input['query']);
header('Content-Type: application/json');
echo json_encode($result->toArray());
