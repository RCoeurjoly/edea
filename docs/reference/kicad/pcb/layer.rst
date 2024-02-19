Layer
=====

.. module:: edea.kicad.pcb.layer
   :synopsis: Definitions of layer names and types for PCB layers.

.. autodata:: edea.kicad.pcb.layer.CanonicalLayerName
   :annotation: = Literal

.. autofunction:: edea.kicad.pcb.layer.layer_to_list

    Serialize a layer to a list.

   A literal type representing the canonical names of PCB layers.

.. autodata:: edea.kicad.pcb.layer.LayerType
   :annotation: = Literal

   A literal type representing the types of PCB layers.

.. data:: layer_names

   A list of all available layer names defined in :data:`CanonicalLayerName`.

.. data:: layer_types

   A list of all available layer types defined in :data:`LayerType`.