from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'task_name'

    task_name = fields.Char(tracking=1, required=1, size=15)
    assign_to = fields.Many2one('res.partner', required=1, tracking=1)
    description = fields.Text()
    due_date = fields.Date(required=1, tracking=1)
    is_late = fields.Boolean()
    estimated_time = fields.Float()
    spent_time = fields.Float(compute="_compute_spent_time", store=True)
    progress = fields.Float(
        string="Progress (%)",
        compute="_compute_progress",
        store=True
    )
    active = fields.Boolean(default=True)
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed')
    ], default='new', tracking=1)

    lines_ids = fields.One2many('todo.task.line', 'todo_task_id')


    _sql_constraints=[
        ('unique_task_name', 'unique(task_name)', 'Task Already Exist!')
    ]

    @api.constrains('spent_time', 'estimated_time')
    def _check_time_limits(self):
        for rec in self:
            if rec.estimated_time and rec.spent_time > rec.estimated_time:
                raise ValidationError("Spent time can't exceed estimated time!")

    @api.depends('lines_ids.time')
    def _compute_spent_time(self):
        for rec in self:
            rec.spent_time = sum(line.time for line in rec.lines_ids)

    @api.depends('estimated_time', 'spent_time')
    def _compute_progress(self):
        for rec in self:
            if rec.estimated_time:
                rec.progress = (rec.spent_time / rec.estimated_time) * 100
            else:
                rec.progress = 0

    def action_new(self):
        for rec in self:
            rec.status= 'new'
            print("Inside Action New")

    def action_in_progress(self):
        for rec in self:
            rec.status= 'in_progress'
            print("Inside Action IN Progress")

    def action_completed(self):
        for rec in self:
            rec.status= 'completed'
            print("Inside Action Completed")


    def close_task(self):
        for rec in self:
            print("Inside close task server action")
            rec.status = 'closed'

    def check_due_date(self):
        # this variable for read all records because self is refering to todo.task()
        tasks_ids = self.search([])
        # loop on all tasks and make your logic
        for rec in tasks_ids:
            if rec.status in ['completed', 'closed']:
                continue
            elif rec.due_date and rec.due_date < fields.Date.today():
                rec.is_late = True

        print("inside check_due_date()")

class TodoTaskLine(models.Model):
    _name = 'todo.task.line'

    todo_task_id = fields.Many2one('todo.task', required=True, ondelete="cascade")
    date = fields.Date()
    description = fields.Text()
    time = fields.Float()
