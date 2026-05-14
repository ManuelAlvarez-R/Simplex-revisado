package UDeA.simplex_revisado.model.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Restriccion {

    private double[] coeficientes;

    private TipoRestriccion tipo;

    private double ladoDerecho;

}