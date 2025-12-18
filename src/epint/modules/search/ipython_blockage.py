# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


IPYTHON_MAGIC_METHODS = [
    # IPython canary method
    '_ipython_canary_method_should_not_exist_',
    
    # IPython display methods
    '_ipython_display_',
    '_ipython_execute_',
    
    # Representation methods (MIME types)
    '_repr_mimebundle_',
    '_repr_html_',
    '_repr_markdown_',
    '_repr_svg_',
    '_repr_png_',
    '_repr_pdf_',
    '_repr_jpeg_',
    '_repr_jpg_',
    '_repr_latex_',
    '_repr_json_',
    '_repr_javascript_',
    '_repr_text_',
    '_repr_plain_',
    
    # IPython special methods
    '_ipython_kernel_',
    '_ipython_shell_',
    '_ipython_',
    
    # Jupyter/IPython widget methods
    '_ipython_widget_',
    '_jupyter_',
    
    # Rich display methods
    '_repr_pretty_',
    '_repr_',
]

