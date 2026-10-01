El LLM utilizado en desarrollo corresponde a qwen3:1.7b, la evaluación se realizó utilizando como juez a ChatGPT 6 Luna en esfuerzo de razonamiento medio. 

Tener en cuenta lo siguiente, al ejecutar esta primera iteración de ingenieria de prompts, se encontró que hay un problema con RAG, el modelo no está recuperando chunks de paginas mas avanzadas del manual, por lo tanto la comparación no debe realizarse inmediatamente con los archivos baseline_v1.csv y baseline_v1_Ranking. Primero se ha corregido el RAG y se ha actualizado el prompt de chat_prompts.py. Los archivos a comparar directamente son:

1.
2.
3.
4.
5.
...



# Protocolo de evaluación LemurCopilot para LLM 

Evalúa cada respuesta sin saber qué versión del prompt la generó.

Usa exclusivamente:
- question
- reference_answer
- qwen_answer
- qwen_sources

No premies similitud textual con la referencia.
Evalúa significado y fidelidad factual.

Métricas de 1 a 5:

Correctness
1 = mayormente incorrecta
2 = varios errores importantes
3 = parcialmente correcta
4 = correcta con detalles menores
5 = completamente correcta

Faithfulness
1 = muchas afirmaciones no respaldadas
2 = varias afirmaciones no respaldadas
3 = mezcla de información respaldada y no respaldada
4 = casi todo respaldado
5 = totalmente respaldada por las fuentes

Completeness
1 = no responde
2 = responde muy poco
3 = responde parcialmente
4 = cubre casi todo
5 = cubre completamente lo necesario

Pedagogy
1 = confusa
2 = difícil de seguir
3 = aceptable
4 = clara y didáctica
5 = excelente explicación para un estudiante

Retrieval quality
1 = fuentes irrelevantes
2 = mayormente irrelevantes
3 = parcialmente relevantes
4 = relevantes
5 = fuentes claramente apropiadas

Para cada fila devuelve:
- scores
- breve justificación
- errores factuales detectados
- afirmaciones no respaldadas