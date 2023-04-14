#lang s-exp framework/keybinding-lang
; Pass this file though Edit > Keybindings > Add User defined Keybindings
(keybinding "c:(" (λ (editor evt) (send editor insert "⟦")))
(keybinding "c:)" (λ (editor evt) (send editor insert "⟧")))
