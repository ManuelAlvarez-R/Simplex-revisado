package UDeA.simplex_revisado.model.entity;

import UDeA.simplex_revisado.model.Enums.TipoVariableEnum;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VariableEntity {

    private String nombre;

    private TipoVariableEnum tipo;

    private double costo;

    private int indice;

}