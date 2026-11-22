from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Produto, Cliente


def inicial(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("Usuário:", username)
        print("Senha:", password)

        user = authenticate(request, username=username, password=password)

        print("Resultado authenticate:", user)

        if user is not None:
            login(request, user)
            print("Login realizado!")
            return redirect('dashboard')

        print("Usuário ou senha inválidos")
        return render(
            request,
            'privado/login.html',
            {'erro': 'Usuário ou senha inválidos'}
        )

    return render(request, 'privado/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmar = request.POST.get('confirmar')

        if password != confirmar:
            return render(
                request,
                'privado/cadastro.html',
                {'erro': 'As senhas não coincidem'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'privado/cadastro.html',
                {'erro': 'Usuário já existe'}
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'privado/cadastro.html')


@login_required
def dashboard(request):
    produtos = Produto.objects.all().order_by("-id")
    clientes = Cliente.objects.all().order_by("-id")

    return render(
        request,
        "dashboard.html",
        {
            "produtos": produtos,
            "clientes": clientes
        }
    )


@extend_schema(
    summary="Cadastrar produto",
    description="Cadastra um novo produto no MercadoNex."
)
@api_view(['POST'])
@login_required
def cadastrar_produto(request):
    if request.method == "POST":
        Produto.objects.create(
            nome=request.POST.get("nome"),
            categoria=request.POST.get("categoria"),
            descricao=request.POST.get("descricao"),
            codigo=request.POST.get("codigo"),
            marca=request.POST.get("marca"),
            preco_venda=request.POST.get("preco_venda"),
            preco_custo=request.POST.get("preco_custo") or None,
            quantidade=request.POST.get("quantidade"),
            validade=request.POST.get("validade") or None,
            fornecedor=request.POST.get("fornecedor"),
            status=bool(request.POST.get("status")),
            destaque=bool(request.POST.get("destaque")),
        )

        messages.success(
            request,
            "Produto cadastrado com sucesso!"
        )

        return redirect("dashboard")

    return redirect("dashboard")


@extend_schema(
    summary="Excluir produto",
    description="Exclui um produto pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do produto que será excluído."
        )
    ]
)
@api_view(['DELETE'])
@login_required
def excluir_produto(request, id):
    produto = Produto.objects.get(id=id)

    produto.delete()

    messages.success(
        request,
        "Produto removido com sucesso!"
    )

    return redirect("dashboard")


@extend_schema(
    summary="Editar produto",
    description="Atualiza os dados de um produto pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do produto que será atualizado."
        )
    ]
)
@api_view(['POST'])
@login_required
def editar_produto(request, id):
    produto = get_object_or_404(
        Produto,
        id=id
    )

    if request.method == "POST":
        produto.nome = request.POST.get("nome")
        produto.categoria = request.POST.get("categoria")
        produto.descricao = request.POST.get("descricao")
        produto.codigo = request.POST.get("codigo")
        produto.marca = request.POST.get("marca")
        produto.preco_venda = request.POST.get("preco_venda")
        produto.preco_custo = request.POST.get("preco_custo") or None
        produto.quantidade = request.POST.get("quantidade")
        produto.validade = request.POST.get("validade") or None
        produto.fornecedor = request.POST.get("fornecedor")
        produto.status = bool(request.POST.get("status"))
        produto.destaque = bool(request.POST.get("destaque"))

        produto.save()

        messages.success(
            request,
            "Produto atualizado com sucesso!"
        )

        return redirect("dashboard")

    produtos = Produto.objects.all()

    return render(
        request,
        "dashboard.html",
        {
            "produtos": produtos,
            "produto_edicao": produto
        }
    )


@extend_schema(
    summary="Consultar produto",
    description="Retorna os dados de um produto pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do produto que será consultado."
        )
    ]
)
@api_view(['GET'])
@login_required
def produto_json(request, id):
    produto = get_object_or_404(
        Produto,
        id=id
    )

    return JsonResponse({
        "id": produto.id,
        "nome": produto.nome,
        "categoria": produto.categoria,
        "descricao": produto.descricao,
        "codigo": produto.codigo,
        "marca": produto.marca,
        "preco_venda": str(produto.preco_venda),
        "preco_custo": str(produto.preco_custo or ""),
        "quantidade": produto.quantidade,
        "validade": (
            produto.validade.strftime("%Y-%m-%d")
            if produto.validade
            else ""
        ),
        "fornecedor": produto.fornecedor,
        "status": produto.status,
        "destaque": produto.destaque,
    })


@extend_schema(
    summary="Cadastrar cliente",
    description="Cadastra um novo cliente no MercadoNex."
)
@api_view(['POST'])
@login_required
def cadastrar_cliente(request):
    if request.method == "POST":
        try:
            cliente = Cliente.objects.create(
                nome=request.POST.get("nome"),
                telefone=request.POST.get("telefone"),
                email=request.POST.get("email"),
                cpf=request.POST.get("cpf"),
                endereco=request.POST.get("endereco"),
                limite_fiado=request.POST.get("limite_fiado") or 0,
                ativo_fiado=request.POST.get("ativo_fiado") == "on"
            )

            return JsonResponse({
                "success": True,
                "cliente": {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "telefone": cliente.telefone,
                    "email": cliente.email,
                    "saldo": float(cliente.saldo_fiado),
                    "ativo_fiado": cliente.ativo_fiado,
                }
            })

        except IntegrityError:
            return JsonResponse({
                "success": False,
                "erro": "Já existe um cliente cadastrado com este CPF."
            })

    return JsonResponse({
        "success": False
    })


@extend_schema(
    summary="Excluir cliente",
    description="Exclui um cliente pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do cliente que será excluído."
        )
    ]
)
@api_view(['DELETE'])
@login_required
def excluir_cliente(request, id):
    cliente = get_object_or_404(
        Cliente,
        id=id
    )

    cliente.delete()

    return JsonResponse({
        "success": True,
        "id": id
    })


@extend_schema(
    summary="Editar cliente",
    description="Atualiza os dados de um cliente pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do cliente que será atualizado."
        )
    ]
)
@api_view(['POST'])
@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(
        Cliente,
        id=id
    )

    if request.method == "POST":
        cliente.nome = request.POST.get("nome")
        cliente.telefone = request.POST.get("telefone")
        cliente.email = request.POST.get("email")
        cliente.cpf = request.POST.get("cpf")
        cliente.endereco = request.POST.get("endereco")
        cliente.limite_fiado = request.POST.get("limite_fiado") or 0
        cliente.ativo_fiado = request.POST.get("ativo_fiado") == "on"

        cliente.save()

        return JsonResponse({
            "success": True,
            "cliente": {
                "id": cliente.id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "email": cliente.email,
                "saldo": float(cliente.saldo_fiado),
                "ativo_fiado": cliente.ativo_fiado,
            }
        })

    return JsonResponse({
        "success": False
    })


@extend_schema(
    summary="Consultar cliente",
    description="Retorna os dados de um cliente pelo seu ID.",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID do cliente que será consultado."
        )
    ]
)
@api_view(['GET'])
@login_required
def cliente_json(request, id):
    cliente = Cliente.objects.get(id=id)

    return JsonResponse({
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "email": cliente.email,
        "cpf": cliente.cpf,
        "endereco": cliente.endereco,
        "limite_fiado": float(cliente.limite_fiado),
        "ativo_fiado": cliente.ativo_fiado,
    })