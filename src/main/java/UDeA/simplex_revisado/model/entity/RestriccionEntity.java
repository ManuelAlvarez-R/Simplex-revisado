package UDeA.simplex_revisado.model.entity;

import UDeA.simplex_revisado.model.Enums.TipoRestriccionEnum;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RestriccionEntity {

    private double[] coeficientes;

    private TipoRestriccionEnum tipo;

    private double ladoDerecho;

}