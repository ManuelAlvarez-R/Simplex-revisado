package UDeA.simplex_revisado.model.entity;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

import UDeA.simplex_revisado.model.Enums.TipoOptimizacionEnum;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProgramaPLEntity {

    private TipoOptimizacionEnum tipoOptimizacion;

    private double[] funcionObjetivo;

    private List<RestriccionEntity> restricciones;

}
