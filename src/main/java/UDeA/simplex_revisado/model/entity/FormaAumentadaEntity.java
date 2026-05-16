package UDeA.simplex_revisado.model.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FormaAumentadaEntity {

    private double[][] matrizA;

    private double[] vectorB;

    private double[] funcionObjetivo;

    private List<VariableEntity> variables;

    private List<String> variablesBasicas;

}