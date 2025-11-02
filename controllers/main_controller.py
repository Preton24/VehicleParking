
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta

from models import db
from models.user import User
from models.lot import ParkingLot
from models.slot import ParkingSlot
from models.reservation import Reservation

main_bp = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- User Dashboard and Reservation ---
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        total_users = User.query.count()
        total_lots = ParkingLot.query.count()
        total_slots = ParkingSlot.query.count()
        total_reservations = Reservation.query.count()

        active_reservations = Reservation.query.filter(Reservation.status == 'active').count()
        completed_reservations = Reservation.query.filter(Reservation.status == 'completed').count()
        cancelled_reservations = Reservation.query.filter(Reservation.status == 'cancelled').count()

        lots_with_slots = []
        for lot in ParkingLot.query.all():
            total = len(lot.slots)
            booked = ParkingSlot.query.filter_by(lot_id=lot.id, status='booked').count()
            occupied = ParkingSlot.query.filter_by(lot_id=lot.id, status='occupied').count()
            booked_count = booked + occupied
            available = total - booked_count
            lots_with_slots.append({'lot': lot, 'total': total, 'booked': booked_count, 'available': available})

        return render_template(
            'dashboard.html',
            is_admin=True,
            total_users=total_users,
            total_lots=total_lots,
            total_slots=total_slots,
            total_reservations=total_reservations,
            active_reservations=active_reservations,
            completed_reservations=completed_reservations,
            cancelled_reservations=cancelled_reservations,
            lots_with_slots=lots_with_slots
        )
    else:
        user_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.start_time.desc()).all()

        return render_template(
            'dashboard.html',
            is_admin=False,
            reservations=user_reservations,
            now=datetime.utcnow()
        )

@main_bp.route('/view_parking')
@login_required
def view_parking():
    lots = ParkingLot.query.all()
    lots_data = []
    for lot in lots:
        slots = ParkingSlot.query.filter_by(lot_id=lot.id).all()
        active_reservations = Reservation.query.filter(
            Reservation.slot_id.in_([s.id for s in slots]),
            Reservation.status == 'active'
        ).all()
        slots_with_status = []
        for slot in slots:
            is_reserved = any(res.slot_id == slot.id for res in active_reservations)

            if slot.status == 'maintenance':
                display_status = 'maintenance'
            elif slot.status == 'occupied':
                display_status = 'occupied'
            elif is_reserved:
                display_status = 'booked'
            else:
                display_status = 'available'

            slots_with_status.append({
                'id': slot.id,
                'number': slot.slot_number,
                'status': display_status
            })
        lots_data.append({'lot': lot, 'slots': slots_with_status})
    return render_template('view_parking.html', lots_data=lots_data)


@main_bp.route('/book_slot/<int:slot_id>', methods=['GET', 'POST'])
@login_required
def book_slot(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)

    # Check if the slot is currently occupied or has an active reservation
    if slot.status == 'occupied':
        flash(f'Slot {slot.slot_number} is currently occupied.', 'warning')
        return redirect(url_for('main.view_parking'))
    
    active_reservation = Reservation.query.filter_by(slot_id=slot.id, status='active').first()
    if active_reservation:
        flash(f'Slot {slot.slot_number} is currently booked.', 'warning')
        return redirect(url_for('main.view_parking'))

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip()
        
        if not vehicle_number:
            flash('Vehicle number is required.', 'danger')
            return render_template('book_slot.html', slot=slot)

        # Set start_time to current time
        start_time = datetime.utcnow()
        
        # Set initial end_time to far future (will be updated when slot is released)
        # Using a date far in the future as placeholder since end_time is required
        end_time = datetime.utcnow() + timedelta(days=365*100)  # 100 years in future as placeholder
        
        # Check if slot is still available
        if slot.status == 'occupied':
            flash(f'Slot {slot.slot_number} became unavailable. Please try another slot.', 'warning')
            return redirect(url_for('main.view_parking'))

        # Cost will be calculated when slot is released, set to None initially
        new_reservation = Reservation(
            user_id=current_user.id,
            slot_id=slot.id,
            vehicle_number=vehicle_number,
            start_time=start_time,
            end_time=end_time,
            status='active',
            cost=None  # Will be calculated on release
        )
        
        # Mark slot as occupied
        slot.status = 'occupied'
        
        db.session.add(new_reservation)
        db.session.add(slot)
        db.session.commit()
        
        flash(f'Slot {slot.slot_number} in {slot.lot.name} booked successfully for vehicle {vehicle_number}!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('book_slot.html', slot=slot)

@main_bp.route('/release_slot/<int:reservation_id>')
@login_required
def release_slot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check authorization
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to release this slot.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Check if reservation is active
    if reservation.status != 'active':
        flash('Cannot release a slot that is not active.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Set end_time to current time
    end_time = datetime.utcnow()
    
    # Calculate duration in hours
    duration = end_time - reservation.start_time
    duration_hours = duration.total_seconds() / 3600.0
    
    # Calculate cost (hours * lot.price)
    total_cost = 0
    if reservation.slot and reservation.slot.lot and reservation.slot.lot.price is not None:
        total_cost = reservation.slot.lot.price * duration_hours
    else:
        flash('This parking lot does not have a price set. Cost set to 0.', 'warning')
    
    # Update reservation
    reservation.end_time = end_time
    reservation.cost = total_cost
    reservation.status = 'completed'
    
    # Mark slot as available
    if reservation.slot:
        reservation.slot.status = 'available'
        db.session.add(reservation.slot)
    
    db.session.add(reservation)
    db.session.commit()
    
    flash(f'Slot released successfully! Duration: {duration_hours:.2f} hours. Cost: ₹{total_cost:,.2f}', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/cancel_reservation/<int:reservation_id>')
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to cancel this reservation.', 'danger')
        return redirect(url_for('main.dashboard'))

    if reservation.status != 'active':
        flash('Cannot cancel a reservation that is not active.', 'warning')
    else:
        reservation.status = 'cancelled'
        if reservation.slot:
            reservation.slot.status = 'available'
        db.session.add(reservation)
        db.session.commit()
        flash('Reservation cancelled successfully.', 'info')
    return redirect(url_for('main.dashboard'))

# --- Admin Functionality ---

@main_bp.route('/admin/lots')
@admin_required
def admin_lots():
    lots = ParkingLot.query.all()
    return render_template('admin_lots.html', lots=lots)


@main_bp.route('/admin/add_lot', methods=['GET', 'POST'])
@admin_required
def add_lot():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        price_str = request.form.get('price')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        max_spots_str = request.form.get('maximum_number_of_spots')

        if not name or not location:
            flash('Name and Location are required.', 'danger')
            return render_template('add_edit_lot.html', lot=None)

        existing_lot = ParkingLot.query.filter_by(name=name).first()
        if existing_lot:
            flash('A parking lot with this name already exists.', 'warning')
            return render_template('add_edit_lot.html', lot=None) # Also pass lot=None on error

        price = None
        if price_str:
            try:
                price = float(price_str)
            except ValueError:
                flash('Invalid price format. Please enter a number.', 'danger')
                return render_template('add_edit_lot.html', lot=None) # Pass lot=None on error

        maximum_number_of_spots = None
        if max_spots_str:
            try:
                maximum_number_of_spots = int(max_spots_str)
                if maximum_number_of_spots < 0:
                    flash('Maximum number of spots cannot be negative.', 'danger')
                    return render_template('add_edit_lot.html', lot=None) # Pass lot=None on error
            except ValueError:
                flash('Invalid maximum number of spots format. Please enter a whole number.', 'danger')
                return render_template('add_edit_lot.html', lot=None) # Pass lot=None on error


        new_lot = ParkingLot(
            name=name,
            location=location,
            price=price,
            address=address,
            pin_code=pin_code,
            maximum_number_of_spots=maximum_number_of_spots
        )
        db.session.add(new_lot)
        db.session.commit()
        flash(f'Parking Lot "{name}" added successfully!', 'success')
        return redirect(url_for('main.admin_lots'))
   
    return render_template('add_edit_lot.html', lot=None)

@main_bp.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.name = request.form.get('name')
        lot.location = request.form.get('location')
        price_str = request.form.get('price')
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')
        max_spots_str = request.form.get('maximum_number_of_spots')

        try:
            lot.price = float(price_str) if price_str else None
        except ValueError:
            flash('Invalid price format. Please enter a number.', 'danger')
            return render_template('add_edit_lot.html', lot=lot)

        try:
            lot.maximum_number_of_spots = int(max_spots_str) if max_spots_str else None
            if lot.maximum_number_of_spots is not None and lot.maximum_number_of_spots < 0:
                flash('Maximum number of spots cannot be negative.', 'danger')
                return render_template('add_edit_lot.html', lot=lot)
        except ValueError:
            flash('Invalid maximum number of spots format. Please enter a whole number.', 'danger')
            return render_template('add_edit_lot.html', lot=lot)

        db.session.commit()
        flash(f'Parking Lot "{lot.name}" updated successfully!', 'success')
        return redirect(url_for('main.admin_lots'))

    return render_template('add_edit_lot.html', lot=lot) 

@main_bp.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    try:
        db.session.delete(lot)
        db.session.commit()
        flash(f'Parking Lot "{lot.name}" and all its slots/reservations deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting parking lot: {str(e)}', 'danger')
    return redirect(url_for('main.admin_lots'))


@main_bp.route('/admin/slots/<int:lot_id>')
@admin_required
def admin_slots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    slots = ParkingSlot.query.filter_by(lot_id=lot.id).order_by(ParkingSlot.slot_number).all()
    return render_template('admin_slots.html', lot=lot, slots=slots)

@main_bp.route('/admin/add_slot/<int:lot_id>', methods=['POST'])
@admin_required
def add_slot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    slot_number = request.form.get('slot_number')

    if not slot_number:
        flash('Slot number is required.', 'danger')
        return redirect(url_for('main.admin_slots', lot_id=lot.id))

    existing_slot = ParkingSlot.query.filter_by(lot_id=lot.id, slot_number=slot_number).first()
    if existing_slot:
        flash(f'Slot number "{slot_number}" already exists in {lot.name}.', 'warning')
        return redirect(url_for('main.admin_slots', lot_id=lot.id))

    # Optional: Check if adding this slot exceeds maximum_number_of_spots
    if lot.maximum_number_of_spots is not None:
        current_slots_count = ParkingSlot.query.filter_by(lot_id=lot.id).count()
        if current_slots_count >= lot.maximum_number_of_spots:
            flash(f'Cannot add more slots. Parking lot "{lot.name}" has reached its maximum capacity of {lot.maximum_number_of_spots} spots.', 'danger')
            return redirect(url_for('main.admin_slots', lot_id=lot.id))


    new_slot = ParkingSlot(lot_id=lot.id, slot_number=slot_number, status='available')
    db.session.add(new_slot)
    db.session.commit()
    flash(f'Slot "{slot_number}" added to {lot.name} successfully!', 'success')
    return redirect(url_for('main.admin_slots', lot_id=lot.id))

@main_bp.route('/admin/update_slot_status/<int:slot_id>', methods=['POST'])
@admin_required
def update_slot_status(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)
    new_status = request.form.get('status')
    if new_status in ['available', 'booked', 'maintenance', 'occupied']: # Define allowed statuses
        slot.status = new_status
        db.session.commit()
        flash(f'Slot {slot.slot_number} status updated to "{new_status}".', 'success')
    else:
        flash('Invalid status provided.', 'danger')
    return redirect(url_for('main.admin_slots', lot_id=slot.lot_id))

@main_bp.route('/admin/delete_slot/<int:slot_id>', methods=['POST'])
@admin_required
def delete_slot(slot_id):
    slot = ParkingSlot.query.get_or_404(slot_id)
    lot_id = slot.lot_id
    try:
        # Before deleting slot, consider cancelling any active reservations for it
        # For this example, cascade delete is handled by the model relationship for Reservation
        db.session.delete(slot)
        db.session.commit()
        flash(f'Slot "{slot.slot_number}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting slot: {str(e)}', 'danger')
    return redirect(url_for('main.admin_slots', lot_id=lot_id))

@main_bp.route('/admin/reservations')
@admin_required
def admin_reservations():
    reservations = Reservation.query.order_by(Reservation.start_time.desc()).all()
    return render_template('admin_reservations.html', reservations=reservations, now=datetime.utcnow())