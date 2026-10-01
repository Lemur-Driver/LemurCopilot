El LLM utilizado en desarrollo corresponde a qwen3:1.7b, la evaluación se realizó utilizando como juez a ChatGPT 6 Luna en esfuerzo de razonamiento medio. 

Tener en cuenta lo siguiente, al ejecutar esta primera iteración de ingenieria de prompts, se encontró que hay un problema con RAG, el modelo no está recuperando chunks de paginas mas avanzadas del manual, por lo tanto la comparación no debe realizarse inmediatamente con los archivos baseline_v1.csv y baseline_v1_Ranking. Primero se ha corregido el RAG y se ha actualizado el prompt de chat_prompts.py. Los archivos a comparar directamente son:

1.
2.
3.
4.
5.
...