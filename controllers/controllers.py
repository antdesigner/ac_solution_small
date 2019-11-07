# -*- coding: utf-8 -*-
from odoo import http

# class AcSolutionSmall(http.Controller):
#     @http.route('/ac_solution_small/ac_solution_small/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ac_solution_small/ac_solution_small/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ac_solution_small.listing', {
#             'root': '/ac_solution_small/ac_solution_small',
#             'objects': http.request.env['ac_solution_small.ac_solution_small'].search([]),
#         })

#     @http.route('/ac_solution_small/ac_solution_small/objects/<model("ac_solution_small.ac_solution_small"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ac_solution_small.object', {
#             'object': obj
#         })