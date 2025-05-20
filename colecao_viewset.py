from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Colecao, PublicacaoSeriada, Biblioteca, MeioFisico
from .serializer import colecao_serializer
from rest_framework import generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.utils.decorators import method_decorator


biblioteca_param = openapi.Parameter('biblioteca', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
publicacaoseriada_param = openapi.Parameter('publicacaoseriada', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[biblioteca_param, publicacaoseriada_param],
    responses={200: openapi.Response('', colecao_serializer.ColecaoGETSerializer)}
))
class ColecaoViewSet(ModelViewSet):
    queryset = Colecao.objects.all()
    serializer_class = colecao_serializer.ColecaoSerializer
    # swagger_schema = None

    def list(self, request, *args, **kwargs):
        self.serializer_class = colecao_serializer.ColecaoGETSerializer
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        biblioteca = self.request.query_params.get('biblioteca', None)
        publicacao_seriada = self.request.query_params.get('publicacaoseriada', None)
        queryset = Colecao.objects.all()

        if publicacao_seriada:
            queryset = queryset.filter(publicacao_seriada=publicacao_seriada)

        if biblioteca:
            queryset = queryset.filter(biblioteca=biblioteca)

        return queryset

    def create(self, request, *args, **kwargs):
        publicacao_seriada = request.data.get('publicacao_seriada', None)
        biblioteca = request.data.get('biblioteca', None)
        meio_fisico = request.data.get('meio_fisico', None)
        conteudo = request.data.get('conteudo', None)
        documento = request.data.get('documento', None)
        pbs_obj = PublicacaoSeriada.objects.filter(id=publicacao_seriada).first()
        biblio_obj = Biblioteca.objects.filter(id=biblioteca).first()
        if not publicacao_seriada and not biblioteca:
            return Response({'mensagem': 'ID da Publicação Seriada e da Biblioteca são obrigatórios'})

        if meio_fisico is not None:
            meio_fisico = MeioFisico.objects.filter(id=meio_fisico).first()
            if not meio_fisico:
                return Response({'mensagem': 'O Meio Fisico informado não existe..'})

        colecao = self.queryset.filter(publicacao_seriada=publicacao_seriada, biblioteca=biblioteca).first()
        if colecao:
            if conteudo or conteudo != '':
                colecao.conteudo = conteudo
                colecao.save()
            if documento or documento != '':
                colecao.documento = documento
                colecao.save()
            if meio_fisico:
                colecao.meio_fisico = meio_fisico
                colecao.save()
            return Response({'mensagem': 'Coleção atualizada com sucesso.'})
        else:
            try:
                Colecao.objects.create(
                    publicacao_seriada=pbs_obj,
                    biblioteca=biblio_obj,
                    conteudo=conteudo,
                    documento=documento,
                    meio_fisico=meio_fisico,
                )
                return Response({'mensagem': 'Coleção criada com sucesso.'})
            except Exception as e:
                return Response({'mensagem': f'Erro ao criar a coleção. Exceção: {e}'})


class ColecaoFullList(generics.ListCreateAPIView):
    queryset = Colecao.objects.all()
    serializer_class = colecao_serializer.ColecaoBibliotecaGETSerializer

    def get_queryset(self):
        biblioteca = self.request.GET.get('biblioteca', None)
        publicacao_seriada = self.request.GET.get('publicacaoseriada', None)

        queryset = Colecao.objects.all()

        if publicacao_seriada:
            queryset = queryset.filter(publicacao_seriada=publicacao_seriada)

        if biblioteca:
            queryset = queryset.filter(biblioteca=biblioteca)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return colecao_serializer.ColecaoFullWriteSerializer
        return colecao_serializer.ColecaoBibliotecaGETSerializer


class ColecaoFullDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colecao.objects.all()
    serializer_class = colecao_serializer.ColecaoFullGetSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return colecao_serializer.ColecaoFullWriteSerializer
        return colecao_serializer.ColecaoFullGetSerializer


#from app.helpers.hash_authenticator import AllowedAPIKey
from app.helpers.api_key_permission import AllowedAPIKey

class ColecaoLegacyViewSet(ModelViewSet):
    queryset = Colecao.objects.all()
    serializer_class = colecao_serializer.ColecaoLegacyGETSerializer
    authentication_classes = []
    permission_classes = [AllowedAPIKey]

    def list(self, request, *args, **kwargs):
        self.serializer_class = colecao_serializer.ColecaoLegacyGETSerializer
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        biblioteca = self.request.query_params.get('biblioteca', None)
        publicacao_seriada = self.request.query_params.get('publicacaoseriada', None)
        queryset = Colecao.objects.all()

        if publicacao_seriada:
            queryset = queryset.filter(publicacao_seriada=publicacao_seriada)

        if biblioteca:
            queryset = queryset.filter(biblioteca=biblioteca)

        return queryset


biblioteca_param = openapi.Parameter('biblioteca', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
publicacao_seriada_param = openapi.Parameter('publicacao_seriada', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
publicacao_param = openapi.Parameter('publicacao', openapi.IN_QUERY, type=openapi.TYPE_STRING)

@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[biblioteca_param, publicacaoseriada_param, publicacao_param],
    responses={200: openapi.Response('', colecao_serializer.ColecaoGETSerializer)}
))
class ColecaoLegacyViewSetFormatted(APIView):
    queryset = Colecao.objects.all()
    serializer_class = colecao_serializer.ColecaoLegacyGETSerializer
    permission_classes = [AllowedAPIKey]
    authentication_classes = []

    def get(self, request, format=None):
        biblioteca = request.GET.get('biblioteca', None)
        publicacao_seriada = request.GET.get('publicacaoseriada', None)
        publicacao = request.GET.get('publicacao', None)
        queryset = Colecao.objects.all()

        if publicacao_seriada:
            queryset = queryset.filter(publicacao_seriada=publicacao_seriada)

        if publicacao:
            queryset = queryset.filter(publicacao_seriada__codigo_ccn=publicacao)

        if biblioteca:
            queryset = queryset.filter(biblioteca=biblioteca)

        serializer = self.serializer_class(queryset, many=True)

        data = serializer.data
        resposta = list()

        for item in data:
            for ic in item['conteudo']:
                if not any(si['ano'] == ic['ano'] for si in resposta):
                    resposta.append({
                        "ano": ic['ano'],
                        "volume-fasciculo": []
                    })

        for item in data:
            for ic in item['conteudo']:
                for ir in resposta:
                    if ic['ano'] == ir["ano"]:
                        if any(vf["transcricao"] == ic["volume-fasciculo"] for vf in ir["volume-fasciculo"]):
                            for vf in ir["volume-fasciculo"]:
                                if vf["transcricao"] == 'nan':
                                    pass
                                if vf["transcricao"] == ic["volume-fasciculo"]:
                                    vf['bibliotecas'].append(item['biblioteca'])
                        else:
                            ir["volume-fasciculo"].append({
                                "transcricao": ic["volume-fasciculo"] if isinstance(ic["volume-fasciculo"], str) else '',
                                "bibliotecas": [item['biblioteca'],]
                            })

        return Response({"colecoes": sorted(resposta, key=lambda x: x["ano"])})