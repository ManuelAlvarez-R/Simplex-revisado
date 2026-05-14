package UDeA.simplex_revisado.model.entity;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

import UDeA.simplex_revisado.model.Enums.EstadoSolucionEnum;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResultadoSimplexEntity {

    private EstadoSolucionEnum estado;

    private double valorOptimo;

    private Map<String, Double> solucion;

    private List<IteracionEntity> iteraciones;

}