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
public class IteracionEntity {

    private int numeroIteracion;

    private List<String> variablesBasicas;

    private List<String> variablesNoBasicas;

    private double[][] matrizB;

    private double[][] matrizBinversa;

    private double[] solucionBasica;

    private double[] costosReducidos;

    private String variableEntrante;

    private String variableSaliente;

    private double valorZ;

}